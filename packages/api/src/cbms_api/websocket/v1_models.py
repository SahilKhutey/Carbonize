"""
cbms_api/websocket/v1_models.py

WebSocket v1 protocol models — Pydantic v2.

These models are the SINGLE SOURCE OF TRUTH for the WebSocket protocol.
JSON Schema is generated from them; TypeScript types are derived
from the JSON Schema via codegen.

Protocol version: 1.0
Subprotocol:      cbms-twin.v1
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# =============================================================================
# CONSTANTS
# =============================================================================

PROTOCOL_VERSION = "1.0"
PROTOCOL_SUBPROTOCOL = "cbms-twin.v1"
_MAJOR_VERSION = int(PROTOCOL_VERSION.split(".")[0])


# =============================================================================
# ENUMS
# =============================================================================


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommandType(str, Enum):
    SET_SETPOINT = "set_setpoint"
    START_EQUIPMENT = "start_equipment"
    STOP_EQUIPMENT = "stop_equipment"
    ACKNOWLEDGE_ALERT = "acknowledge_alert"


class CommandAckStatus(str, Enum):
    SUCCESS = "success"
    REJECTED = "rejected"
    ERROR = "error"


class GoodbyeReason(str, Enum):
    SERVER_SHUTDOWN = "server_shutdown"
    AUTH_EXPIRED = "auth_expired"
    RATE_LIMITED = "rate_limited"
    NORMAL = "normal"
    UNAUTHORIZED = "unauthorized"


class OperatingMode(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAULT = "fault"
    MAINTENANCE = "maintenance"


class ErrorCode(str, Enum):
    INVALID_MESSAGE = "INVALID_MESSAGE"
    UNKNOWN_TYPE = "UNKNOWN_TYPE"
    RATE_LIMITED = "RATE_LIMITED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_COMMAND = "INVALID_COMMAND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# =============================================================================
# BASE ENVELOPE
# =============================================================================


class MessageBase(BaseModel):
    """Base class for all WebSocket messages."""

    model_config = ConfigDict(
        extra="ignore",  # Forward-compatible: unknown fields silently ignored
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    type: str = Field(..., min_length=1, max_length=64, description="Message type discriminator")
    version: str = Field(
        default=PROTOCOL_VERSION,
        pattern=r"^\d+\.\d+$",
        description="Protocol version (major.minor)",
    )
    id: UUID = Field(default_factory=uuid4, description="Unique message ID for deduplication")
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Sender timestamp (UTC ISO 8601)",
    )
    seq: int = Field(default=0, ge=0, le=2**31 - 1, description="Monotonic sequence number")

    @field_validator("version", mode="after")
    @classmethod
    def validate_version_compat(cls, v: str) -> str:
        """Reject messages from a newer major version that we cannot parse."""
        try:
            major = int(v.split(".")[0])
        except (ValueError, IndexError):
            raise ValueError(f"Malformed version: {v!r}")
        if major > _MAJOR_VERSION:
            raise ValueError(
                f"Message version {v!r} is newer than supported {PROTOCOL_VERSION!r}"
            )
        return v


# =============================================================================
# DATA PAYLOADS
# =============================================================================


class WelcomeData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    connection_id: UUID = Field(description="Server-assigned connection ID")
    plant_id: UUID = Field(description="Plant being streamed")
    org_id: UUID = Field(description="Tenant org ID (from JWT)")
    initial_state: dict[str, Any] = Field(
        default_factory=dict, description="Current TwinState snapshot"
    )
    server_time: datetime = Field(description="Server clock for client synchronisation")
    reconnect_token: str = Field(
        ..., min_length=16, max_length=512,
        description="Opaque token for session resumption"
    )
    tick_interval_seconds: int = Field(default=5, ge=1, le=60, description="Default tick rate")


class SubscribeData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tick_interval_seconds: Optional[int] = Field(default=None, ge=1, le=60)
    include_alerts: Optional[bool] = Field(default=None)
    include_predictions: Optional[bool] = Field(default=None)
    resume_from_seq: Optional[int] = Field(default=None, ge=0)
    reconnect_token: Optional[str] = Field(default=None, min_length=16, max_length=512)


class ActualsData(BaseModel):
    """Live sensor readings. Extra fields allowed for forward-compat."""
    model_config = ConfigDict(extra="allow")

    co2_inlet_pct: Optional[float] = Field(default=None, ge=0, le=100)
    co2_outlet_pct: Optional[float] = Field(default=None, ge=0, le=100)
    so2_inlet_mg_nm3: Optional[float] = Field(default=None, ge=0)
    so2_outlet_mg_nm3: Optional[float] = Field(default=None, ge=0)
    mesh_dp_mmH2O: Optional[float] = Field(default=None)
    reactor_temp_c: Optional[float] = Field(default=None)


class PerformanceData(BaseModel):
    """Computed performance metrics."""
    model_config = ConfigDict(extra="allow")

    co2_capture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    so2_capture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    energy_consumption_kw: Optional[float] = Field(default=None, ge=0)


class MaintenancePrediction(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = Field(..., min_length=1, max_length=64)
    predicted_at: datetime


class TickData(BaseModel):
    """Periodic state update — sent every N seconds."""
    model_config = ConfigDict(extra="ignore")

    operating_mode: OperatingMode = OperatingMode.IDLE
    current_actuals: ActualsData = Field(default_factory=ActualsData)
    current_setpoints: dict[str, Any] = Field(default_factory=dict)
    performance: PerformanceData = Field(default_factory=PerformanceData)
    next_maintenance: Optional[MaintenancePrediction] = None
    uptime_seconds: float = Field(default=0.0, ge=0)


class AlertData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alert_id: UUID
    severity: AlertSeverity
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    metric: Optional[str] = Field(default=None, max_length=64)
    value: Optional[float] = None
    threshold: Optional[float] = None
    triggered_at: datetime
    recommended_action: Optional[str] = Field(default=None, max_length=500)


class AlertClearedData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alert_id: UUID
    cleared_at: datetime
    auto_resolved: bool = False


class CommandData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    command: CommandType
    target: Optional[str] = Field(default=None, max_length=128)
    value: Optional[Union[float, str, bool]] = None
    equipment_id: Optional[str] = Field(default=None, max_length=128)
    alert_id: Optional[UUID] = None
    reason: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_command_fields(self) -> "CommandData":
        if self.command == CommandType.SET_SETPOINT:
            if self.target is None:
                raise ValueError("`target` is required for set_setpoint command")
            if self.value is None:
                raise ValueError("`value` is required for set_setpoint command")
        if self.command in (CommandType.START_EQUIPMENT, CommandType.STOP_EQUIPMENT):
            if self.target is None and self.equipment_id is None:
                raise ValueError(
                    "`target` or `equipment_id` required for start/stop_equipment"
                )
        if self.command == CommandType.ACKNOWLEDGE_ALERT:
            if self.alert_id is None:
                raise ValueError("`alert_id` is required for acknowledge_alert command")
        return self


class CommandAckData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    command_id: UUID = Field(description="Echoes the originating client message ID")
    status: CommandAckStatus
    error: Optional[str] = Field(default=None, max_length=500)
    new_state: Optional[dict[str, Any]] = None


class PingData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    client_ts: Optional[datetime] = None


class PongData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    client_ts: Optional[datetime] = Field(
        default=None, description="Echoed from ping for RTT calculation"
    )
    rtt_ms: Optional[float] = Field(default=None, ge=0)


class ErrorData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: ErrorCode
    message: str = Field(..., min_length=1, max_length=500)
    fatal: bool = Field(default=False, description="If true, client should not attempt reconnect")


class GoodbyeData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    reason: GoodbyeReason
    reconnect_after_seconds: int = Field(default=5, ge=0, le=300)
    message: Optional[str] = Field(default=None, max_length=200)


class ResumeData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    from_seq: int = Field(..., ge=0, description="Last sequence number client received")
    reconnect_token: str = Field(..., min_length=16, max_length=512)


# =============================================================================
# TYPED MESSAGE WRAPPERS
# =============================================================================


class WelcomeMessage(MessageBase):
    type: Literal["welcome"] = "welcome"
    data: WelcomeData


class SubscribeMessage(MessageBase):
    type: Literal["subscribe"] = "subscribe"
    data: SubscribeData = Field(default_factory=SubscribeData)


class TickMessage(MessageBase):
    type: Literal["tick"] = "tick"
    data: TickData


class AlertMessage(MessageBase):
    type: Literal["alert"] = "alert"
    data: AlertData


class AlertClearedMessage(MessageBase):
    type: Literal["alert_cleared"] = "alert_cleared"
    data: AlertClearedData


class CommandMessage(MessageBase):
    type: Literal["command"] = "command"
    data: CommandData


class CommandAckMessage(MessageBase):
    type: Literal["command_ack"] = "command_ack"
    data: CommandAckData


class PingMessage(MessageBase):
    type: Literal["ping"] = "ping"
    data: PingData = Field(default_factory=PingData)


class PongMessage(MessageBase):
    type: Literal["pong"] = "pong"
    data: PongData = Field(default_factory=PongData)


class ErrorMessage(MessageBase):
    type: Literal["error"] = "error"
    data: ErrorData


class GoodbyeMessage(MessageBase):
    type: Literal["goodbye"] = "goodbye"
    data: GoodbyeData


class ResumeMessage(MessageBase):
    type: Literal["resume"] = "resume"
    data: ResumeData


# Discriminated union — every valid message on the wire
AnyMessage = Union[
    WelcomeMessage,
    SubscribeMessage,
    TickMessage,
    AlertMessage,
    AlertClearedMessage,
    CommandMessage,
    CommandAckMessage,
    PingMessage,
    PongMessage,
    ErrorMessage,
    GoodbyeMessage,
    ResumeMessage,
]

ServerMessage = Union[
    WelcomeMessage,
    TickMessage,
    AlertMessage,
    AlertClearedMessage,
    CommandAckMessage,
    PongMessage,
    ErrorMessage,
    GoodbyeMessage,
]

ClientMessage = Union[
    SubscribeMessage,
    CommandMessage,
    PingMessage,
    ResumeMessage,
]

# Dispatch table: type string → model class
_TYPE_MAP: dict[str, type[MessageBase]] = {
    "welcome": WelcomeMessage,
    "subscribe": SubscribeMessage,
    "tick": TickMessage,
    "alert": AlertMessage,
    "alert_cleared": AlertClearedMessage,
    "command": CommandMessage,
    "command_ack": CommandAckMessage,
    "ping": PingMessage,
    "pong": PongMessage,
    "error": ErrorMessage,
    "goodbye": GoodbyeMessage,
    "resume": ResumeMessage,
}


# =============================================================================
# SERIALIZATION / DESERIALIZATION
# =============================================================================


def serialize_message(msg: MessageBase) -> str:
    """Serialize a Pydantic message to a JSON string (wire format)."""
    return msg.model_dump_json()


def deserialize_message(data: "str | bytes | dict[str, Any]") -> AnyMessage:
    """
    Parse an incoming WebSocket frame into a typed Pydantic message.

    Raises:
        ValueError:                Missing `type` field or unknown type string.
        pydantic.ValidationError:  Schema mismatch in the payload.
    """
    if isinstance(data, (str, bytes)):
        raw: dict[str, Any] = json.loads(data)
    else:
        raw = dict(data)

    msg_type = raw.get("type")
    if msg_type is None:
        raise ValueError("Missing required field: 'type'")

    model_cls = _TYPE_MAP.get(str(msg_type))
    if model_cls is None:
        raise ValueError(f"Unknown message type: {msg_type!r}")

    return model_cls.model_validate(raw)


def make_error_message(
    code: ErrorCode,
    message: str,
    *,
    fatal: bool = False,
    seq: int = 0,
) -> ErrorMessage:
    """Convenience factory for error messages."""
    return ErrorMessage(seq=seq, data=ErrorData(code=code, message=message, fatal=fatal))
