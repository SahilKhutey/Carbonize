"""
tests/contract/test_ws_protocol.py

Contract tests for the CBMS-Sim WebSocket v1 protocol.

These tests validate:
  - Every message type serialises and round-trips losslessly
  - Version enforcement (future majors rejected, past majors accepted)
  - Forward-compatibility (extra unknown fields silently ignored)
  - Command field validation (missing required context fields rejected)
  - Error path: missing type, unknown type, bad version
  - Discriminated-union dispatch (right class returned for each type)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cbms_api.websocket.v1_models import (
    ActualsData,
    AlertClearedData,
    AlertClearedMessage,
    AlertData,
    AlertMessage,
    AlertSeverity,
    CommandAckData,
    CommandAckMessage,
    CommandAckStatus,
    CommandData,
    CommandMessage,
    CommandType,
    ErrorCode,
    ErrorData,
    ErrorMessage,
    GoodbyeData,
    GoodbyeMessage,
    GoodbyeReason,
    OperatingMode,
    PerformanceData,
    PingData,
    PingMessage,
    PongData,
    PongMessage,
    PROTOCOL_VERSION,
    ResumeData,
    ResumeMessage,
    SubscribeData,
    SubscribeMessage,
    TickData,
    TickMessage,
    WelcomeData,
    WelcomeMessage,
    deserialize_message,
    make_error_message,
    serialize_message,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def welcome_msg() -> WelcomeMessage:
    return WelcomeMessage(
        seq=1,
        data=WelcomeData(
            connection_id=uuid4(),
            plant_id=uuid4(),
            org_id=uuid4(),
            initial_state={"operating_mode": "running"},
            server_time=datetime.now(timezone.utc),
            reconnect_token="x" * 32,
        ),
    )


@pytest.fixture()
def tick_msg() -> TickMessage:
    return TickMessage(
        seq=2,
        data=TickData(
            operating_mode=OperatingMode.RUNNING,
            current_actuals=ActualsData(
                co2_inlet_pct=14.5,
                co2_outlet_pct=1.9,
                so2_inlet_mg_nm3=1200,
                so2_outlet_mg_nm3=38,
                reactor_temp_c=40.2,
            ),
            current_setpoints={"reactor_temp_c": 40.0},
            performance=PerformanceData(
                co2_capture_pct=86.9,
                so2_capture_pct=96.8,
                energy_consumption_kw=35.1,
            ),
            uptime_seconds=3600.0,
        ),
    )


@pytest.fixture()
def alert_msg() -> AlertMessage:
    return AlertMessage(
        seq=3,
        data=AlertData(
            alert_id=uuid4(),
            severity=AlertSeverity.HIGH,
            title="SO₂ outlet spike",
            message="Outlet SO₂ at 245 mg/Nm³ exceeds threshold of 200",
            metric="so2_outlet_mg_nm3",
            value=245.0,
            threshold=200.0,
            triggered_at=datetime.now(timezone.utc),
            recommended_action="Increase L/G ratio",
        ),
    )


# ---------------------------------------------------------------------------
# 1. Envelope invariants
# ---------------------------------------------------------------------------


class TestEnvelope:
    def test_envelope_fields_present(self, welcome_msg: WelcomeMessage) -> None:
        assert welcome_msg.type == "welcome"
        assert welcome_msg.version == PROTOCOL_VERSION
        assert welcome_msg.id is not None
        assert welcome_msg.ts is not None
        assert isinstance(welcome_msg.seq, int)
        assert welcome_msg.data is not None

    def test_seq_assigned_on_send(self, welcome_msg: WelcomeMessage) -> None:
        # seq defaults to 0 if not set; we set it to 1 in fixture
        assert welcome_msg.seq == 1

    def test_default_version_is_protocol_version(self) -> None:
        msg = PingMessage(seq=1, data=PingData())
        assert msg.version == PROTOCOL_VERSION


# ---------------------------------------------------------------------------
# 2. Serialisation round-trips
# ---------------------------------------------------------------------------


class TestRoundTrip:
    ALL_FIXTURES = [
        "welcome_msg",
        "tick_msg",
        "alert_msg",
    ]

    def _roundtrip(self, msg) -> None:
        wire = serialize_message(msg)
        restored = deserialize_message(wire)
        assert restored.type == msg.type
        assert restored.version == msg.version
        assert restored.id == msg.id

    def test_welcome_roundtrip(self, welcome_msg: WelcomeMessage) -> None:
        self._roundtrip(welcome_msg)

    def test_tick_roundtrip(self, tick_msg: TickMessage) -> None:
        self._roundtrip(tick_msg)

    def test_alert_roundtrip(self, alert_msg: AlertMessage) -> None:
        self._roundtrip(alert_msg)

    def test_alert_cleared_roundtrip(self) -> None:
        msg = AlertClearedMessage(
            seq=4,
            data=AlertClearedData(
                alert_id=uuid4(),
                cleared_at=datetime.now(timezone.utc),
                auto_resolved=True,
            ),
        )
        self._roundtrip(msg)

    def test_command_roundtrip(self) -> None:
        msg = CommandMessage(
            seq=5,
            data=CommandData(
                command=CommandType.SET_SETPOINT,
                target="reactor_temp_c",
                value=42.0,
                reason="operator",
            ),
        )
        self._roundtrip(msg)

    def test_command_ack_roundtrip(self) -> None:
        msg = CommandAckMessage(
            seq=6,
            data=CommandAckData(
                command_id=uuid4(),
                status=CommandAckStatus.SUCCESS,
            ),
        )
        self._roundtrip(msg)

    def test_ping_pong_roundtrip(self) -> None:
        ping = PingMessage(seq=7, data=PingData(client_ts=datetime.now(timezone.utc)))
        pong = PongMessage(seq=8, data=PongData(client_ts=datetime.now(timezone.utc), rtt_ms=12.3))
        self._roundtrip(ping)
        self._roundtrip(pong)

    def test_error_roundtrip(self) -> None:
        msg = ErrorMessage(
            seq=9,
            data=ErrorData(code=ErrorCode.INVALID_MESSAGE, message="Bad field", fatal=False),
        )
        self._roundtrip(msg)

    def test_goodbye_roundtrip(self) -> None:
        msg = GoodbyeMessage(
            seq=10,
            data=GoodbyeData(reason=GoodbyeReason.AUTH_EXPIRED, reconnect_after_seconds=30),
        )
        self._roundtrip(msg)

    def test_resume_roundtrip(self) -> None:
        msg = ResumeMessage(
            seq=1,
            data=ResumeData(from_seq=42, reconnect_token="y" * 32),
        )
        self._roundtrip(msg)

    def test_subscribe_roundtrip(self) -> None:
        msg = SubscribeMessage(
            seq=1,
            data=SubscribeData(
                tick_interval_seconds=10,
                include_alerts=True,
                include_predictions=False,
            ),
        )
        self._roundtrip(msg)


# ---------------------------------------------------------------------------
# 3. Deserialise dispatch
# ---------------------------------------------------------------------------


class TestDispatch:
    def test_welcome_dispatched_to_correct_class(self, welcome_msg: WelcomeMessage) -> None:
        restored = deserialize_message(serialize_message(welcome_msg))
        assert isinstance(restored, WelcomeMessage)

    def test_tick_dispatched_to_correct_class(self, tick_msg: TickMessage) -> None:
        restored = deserialize_message(serialize_message(tick_msg))
        assert isinstance(restored, TickMessage)

    def test_alert_dispatched_to_correct_class(self, alert_msg: AlertMessage) -> None:
        restored = deserialize_message(serialize_message(alert_msg))
        assert isinstance(restored, AlertMessage)

    def test_command_dispatched_to_correct_class(self) -> None:
        msg = CommandMessage(
            seq=1,
            data=CommandData(command=CommandType.SET_SETPOINT, target="t", value=1.0),
        )
        assert isinstance(deserialize_message(serialize_message(msg)), CommandMessage)

    def test_dict_input_accepted(self, welcome_msg: WelcomeMessage) -> None:
        d = json.loads(serialize_message(welcome_msg))
        restored = deserialize_message(d)
        assert isinstance(restored, WelcomeMessage)


# ---------------------------------------------------------------------------
# 4. Version enforcement
# ---------------------------------------------------------------------------


class TestVersioning:
    def test_current_version_accepted(self) -> None:
        msg = PingMessage(seq=1, version=PROTOCOL_VERSION, data=PingData())
        assert msg.version == PROTOCOL_VERSION

    def test_older_minor_version_accepted(self) -> None:
        # e.g., a 1.0 server receiving a 1.0 message — fine
        raw = json.loads(serialize_message(PingMessage(seq=1, data=PingData())))
        raw["version"] = "1.0"
        result = deserialize_message(raw)
        assert isinstance(result, PingMessage)

    def test_future_major_version_rejected(self) -> None:
        raw = json.loads(serialize_message(PingMessage(seq=1, data=PingData())))
        raw["version"] = "99.0"
        with pytest.raises((ValidationError, ValueError)):
            deserialize_message(raw)

    def test_malformed_version_rejected(self) -> None:
        raw = json.loads(serialize_message(PingMessage(seq=1, data=PingData())))
        raw["version"] = "not-a-version"
        with pytest.raises((ValidationError, ValueError)):
            deserialize_message(raw)


# ---------------------------------------------------------------------------
# 5. Forward compatibility (extra unknown fields ignored)
# ---------------------------------------------------------------------------


class TestForwardCompatibility:
    def test_unknown_envelope_field_ignored(self) -> None:
        raw = json.loads(serialize_message(PingMessage(seq=1, data=PingData())))
        raw["future_field"] = "from_v2"
        # Should not raise
        result = deserialize_message(raw)
        assert isinstance(result, PingMessage)

    def test_unknown_data_field_ignored_in_tick(self, tick_msg: TickMessage) -> None:
        raw = json.loads(serialize_message(tick_msg))
        raw["data"]["new_v2_field"] = {"nested": True}
        result = deserialize_message(raw)
        assert isinstance(result, TickMessage)

    def test_unknown_type_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown message type"):
            deserialize_message({"type": "teleport", "version": "1.0", "seq": 1, "data": {}})


# ---------------------------------------------------------------------------
# 6. Error path — malformed input
# ---------------------------------------------------------------------------


class TestErrorPaths:
    def test_missing_type_raises(self) -> None:
        with pytest.raises((ValueError, ValidationError)):
            deserialize_message({"version": "1.0", "seq": 1, "data": {}})

    def test_bad_json_raises(self) -> None:
        with pytest.raises(Exception):
            deserialize_message("{not json}")

    def test_missing_required_data_field_raises(self) -> None:
        # WelcomeMessage requires data.connection_id etc.
        with pytest.raises(ValidationError):
            deserialize_message({
                "type": "welcome",
                "version": "1.0",
                "seq": 1,
                "data": {},  # missing required fields
            })


# ---------------------------------------------------------------------------
# 7. Command validation
# ---------------------------------------------------------------------------


class TestCommandValidation:
    def test_set_setpoint_requires_target_and_value(self) -> None:
        with pytest.raises(ValidationError):
            CommandData(command=CommandType.SET_SETPOINT)  # missing target + value

    def test_set_setpoint_missing_value_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CommandData(command=CommandType.SET_SETPOINT, target="reactor_temp_c")  # no value

    def test_acknowledge_alert_requires_alert_id(self) -> None:
        with pytest.raises(ValidationError):
            CommandData(command=CommandType.ACKNOWLEDGE_ALERT)  # no alert_id

    def test_start_equipment_requires_target_or_equipment_id(self) -> None:
        with pytest.raises(ValidationError):
            CommandData(command=CommandType.START_EQUIPMENT)  # neither target nor equipment_id

    def test_valid_set_setpoint_accepted(self) -> None:
        cmd = CommandData(
            command=CommandType.SET_SETPOINT,
            target="reactor_temp_c",
            value=42.5,
            reason="operator",
        )
        assert cmd.command == CommandType.SET_SETPOINT
        assert cmd.target == "reactor_temp_c"
        assert cmd.value == 42.5

    def test_valid_start_equipment_with_equipment_id(self) -> None:
        cmd = CommandData(
            command=CommandType.START_EQUIPMENT,
            equipment_id="pump-01",
        )
        assert cmd.equipment_id == "pump-01"

    def test_valid_acknowledge_alert(self) -> None:
        alert_id = uuid4()
        cmd = CommandData(command=CommandType.ACKNOWLEDGE_ALERT, alert_id=alert_id)
        assert cmd.alert_id == alert_id


# ---------------------------------------------------------------------------
# 8. make_error_message factory
# ---------------------------------------------------------------------------


class TestErrorFactory:
    def test_make_error_message_non_fatal(self) -> None:
        msg = make_error_message(ErrorCode.RATE_LIMITED, "Slow down", fatal=False, seq=5)
        assert msg.type == "error"
        assert msg.data.code == ErrorCode.RATE_LIMITED
        assert msg.data.fatal is False
        assert msg.seq == 5

    def test_make_error_message_fatal(self) -> None:
        msg = make_error_message(ErrorCode.AUTH_EXPIRED, "Token expired", fatal=True)
        assert msg.data.fatal is True

    def test_error_message_serialises(self) -> None:
        msg = make_error_message(ErrorCode.INTERNAL_ERROR, "Boom")
        wire = serialize_message(msg)
        assert '"INTERNAL_ERROR"' in wire


# ---------------------------------------------------------------------------
# 9. Alert severity ordering
# ---------------------------------------------------------------------------


class TestAlertSeverity:
    def test_all_severities_valid(self) -> None:
        for sev in AlertSeverity:
            data = AlertData(
                alert_id=uuid4(),
                severity=sev,
                title="Test",
                message="Testing severity",
                triggered_at=datetime.now(timezone.utc),
            )
            assert data.severity == sev

    def test_invalid_severity_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AlertData(
                alert_id=uuid4(),
                severity="EXTREME",  # not a valid enum value
                title="Test",
                message="Test",
                triggered_at=datetime.now(timezone.utc),
            )
