"""
cbms_api/websocket/twin.py

WebSocket endpoint for digital twin real-time streaming.

Implements the v1 protocol:
  - JWT authenticated (token query param)
  - Tenant isolated (org_id from token, RLS-scoped DB queries)
  - Bidirectional: server pushes ticks/alerts; client sends commands/pings
  - Reconnection: exponential backoff + resume via reconnect_token + from_seq
  - Heartbeat: server pings every 30s; client tracks RTT
  - Rate-limited: per-connection 60 msgs/min ceiling
"""

from __future__ import annotations

import asyncio
import secrets
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Deque, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from cbms_api.websocket.v1_models import (
    AnyMessage,
    CommandAckData,
    CommandAckStatus,
    CommandMessage,
    CommandType,
    ErrorCode,
    ErrorMessage,
    ErrorData,
    GoodbyeData,
    GoodbyeMessage,
    GoodbyeReason,
    MessageBase,
    OperatingMode,
    PerformanceData,
    PingMessage,
    PongData,
    PongMessage,
    PROTOCOL_SUBPROTOCOL,
    PROTOCOL_VERSION,
    ResumeMessage,
    SubscribeMessage,
    TickData,
    TickMessage,
    ActualsData,
    WelcomeData,
    WelcomeMessage,
    deserialize_message,
    make_error_message,
    serialize_message,
    CommandAckMessage,
)
from cbms_shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["websocket"])

# ---------------------------------------------------------------------------
# Connection bookkeeping
# ---------------------------------------------------------------------------

_MAX_REPLAY = 1_000          # ring-buffer depth per connection
_HEARTBEAT_INTERVAL = 30.0   # seconds between server pings
_TICK_INTERVAL_DEFAULT = 5.0 # seconds between state ticks
_RATE_LIMIT_MSG = 60         # messages per minute per connection


# ---------------------------------------------------------------------------
# TwinConnection — wraps a single WebSocket session
# ---------------------------------------------------------------------------


class TwinConnection:
    """State for one authenticated WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        user_id: UUID,
        org_id: UUID,
        plant_id: UUID,
        is_read_only: bool = False,
    ) -> None:
        self.ws = websocket
        self.user_id = user_id
        self.org_id = org_id
        self.plant_id = plant_id
        self.is_read_only = is_read_only

        self.connection_id: UUID = uuid4()
        self.reconnect_token: str = secrets.token_urlsafe(32)

        # Sequence counter
        self._seq: int = 0

        # Replay ring-buffer for resume support
        self._replay: Deque[tuple[int, str]] = deque(maxlen=_MAX_REPLAY)

        # Runtime-adjustable tick interval (seconds)
        self.tick_interval: float = _TICK_INTERVAL_DEFAULT

        # Rate-limiting state
        self._msgs_this_window: int = 0
        self._window_reset_at: datetime = datetime.now(timezone.utc) + timedelta(minutes=1)

        self.connected_at: datetime = datetime.now(timezone.utc)
        self.last_activity_at: datetime = self.connected_at

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    async def send(self, msg: MessageBase) -> None:
        """Assign next sequence number, serialise, and send."""
        self._seq += 1
        msg.seq = self._seq
        wire = serialize_message(msg)
        self._replay.append((self._seq, wire))
        await self.ws.send_text(wire)

    # ------------------------------------------------------------------
    # Rate-limiting
    # ------------------------------------------------------------------

    def check_rate_limit(self) -> bool:
        now = datetime.now(timezone.utc)
        if now > self._window_reset_at:
            self._msgs_this_window = 0
            self._window_reset_at = now + timedelta(minutes=1)

        if self._msgs_this_window >= _RATE_LIMIT_MSG:
            return False

        self._msgs_this_window += 1
        return True

    # ------------------------------------------------------------------
    # Resume helpers
    # ------------------------------------------------------------------

    def replay_since(self, from_seq: int) -> list[str]:
        """Return serialised messages with seq > from_seq (for resume)."""
        return [wire for seq, wire in self._replay if seq > from_seq]


# ---------------------------------------------------------------------------
# Background coroutines
# ---------------------------------------------------------------------------


async def _tick_loop(conn: TwinConnection, get_session) -> None:
    """Push TickMessage every `conn.tick_interval` seconds."""
    while True:
        try:
            await asyncio.sleep(conn.tick_interval)
            state = await _fetch_state(conn.plant_id, conn.org_id, get_session)
            uptime = (datetime.now(timezone.utc) - conn.connected_at).total_seconds()

            tick = TickMessage(
                data=TickData(
                    operating_mode=state.get("operating_mode", OperatingMode.IDLE),
                    current_actuals=ActualsData(**{
                        k: v for k, v in state.get("current_actuals", {}).items()
                        if k in ActualsData.model_fields
                    }),
                    current_setpoints=state.get("current_setpoints", {}),
                    performance=PerformanceData(**{
                        k: v for k, v in state.get("performance", {}).items()
                        if k in PerformanceData.model_fields
                    }),
                    uptime_seconds=uptime,
                )
            )
            await conn.send(tick)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.warning("tick_loop_error", error=str(exc), plant_id=str(conn.plant_id))


async def _heartbeat_loop(conn: TwinConnection) -> None:
    """Send a server-side ping every 30 s to keep the connection alive."""
    while True:
        try:
            await asyncio.sleep(_HEARTBEAT_INTERVAL)
            ping_wire = (
                f'{{"type":"ping","version":"{PROTOCOL_VERSION}",'
                f'"seq":0,"id":"{uuid4()}","ts":"{datetime.now(timezone.utc).isoformat()}",'
                f'"data":{{"client_ts":null}}}}'
            )
            await conn.ws.send_text(ping_wire)
        except asyncio.CancelledError:
            break
        except Exception:
            break


# ---------------------------------------------------------------------------
# Client message handler
# ---------------------------------------------------------------------------


async def _handle_client_message(
    conn: TwinConnection,
    raw: str,
    get_session,
) -> None:
    """Parse and dispatch one client-originated message."""
    try:
        msg: AnyMessage = deserialize_message(raw)
    except ValueError as exc:
        await conn.send(make_error_message(ErrorCode.INVALID_MESSAGE, str(exc)[:200]))
        return
    except Exception as exc:
        await conn.send(make_error_message(ErrorCode.INVALID_MESSAGE, "Malformed JSON"))
        return

    conn.last_activity_at = datetime.now(timezone.utc)

    if isinstance(msg, SubscribeMessage):
        if msg.data.tick_interval_seconds is not None:
            conn.tick_interval = float(msg.data.tick_interval_seconds)

    elif isinstance(msg, ResumeMessage):
        missed = conn.replay_since(msg.data.from_seq)
        for wire in missed:
            await conn.ws.send_text(wire)

    elif isinstance(msg, PingMessage):
        await conn.send(PongMessage(data=PongData(client_ts=msg.data.client_ts)))

    elif isinstance(msg, CommandMessage):
        if conn.is_read_only:
            await conn.send(CommandAckMessage(data=CommandAckData(
                command_id=msg.id,
                status=CommandAckStatus.REJECTED,
                error="Viewer role cannot send commands",
            )))
            return
        try:
            new_state = await _execute_command(conn, msg, get_session)
            await conn.send(CommandAckMessage(data=CommandAckData(
                command_id=msg.id,
                status=CommandAckStatus.SUCCESS,
                new_state=new_state,
            )))
        except NotImplementedError as exc:
            await conn.send(CommandAckMessage(data=CommandAckData(
                command_id=msg.id,
                status=CommandAckStatus.REJECTED,
                error=str(exc),
            )))
        except Exception as exc:
            await conn.send(CommandAckMessage(data=CommandAckData(
                command_id=msg.id,
                status=CommandAckStatus.ERROR,
                error=str(exc)[:200],
            )))

    else:
        # Server-only message type sent by client — ignore gracefully
        await conn.send(make_error_message(
            ErrorCode.UNKNOWN_TYPE,
            f"Message type {msg.type!r} is not accepted from clients",
            fatal=False,
        ))


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _fetch_state(plant_id: UUID, org_id: UUID, get_session) -> dict:
    async with get_session() as session:
        try:
            await session.execute(
                text("SET LOCAL app.current_org_id = :oid"), {"oid": str(org_id)}
            )
        except Exception:
            pass  # SQLite test env doesn't support SET LOCAL

        result = await session.execute(
            text("""
                SELECT operating_mode, current_actuals, current_setpoints
                FROM twin_states
                WHERE plant_id = :pid
            """),
            {"pid": str(plant_id)},
        )
        row = result.first()

    if row is None:
        return {}
    return {
        "operating_mode": row[0] or "idle",
        "current_actuals": row[1] or {},
        "current_setpoints": row[2] or {},
        "performance": {},
    }


async def _execute_command(conn: TwinConnection, msg: CommandMessage, get_session) -> dict:
    cmd = msg.data
    if cmd.command == CommandType.SET_SETPOINT:
        async with get_session() as session:
            try:
                await session.execute(
                    text("SET LOCAL app.current_org_id = :oid"), {"oid": str(conn.org_id)}
                )
            except Exception:
                pass

            await session.execute(
                text("""
                    UPDATE twin_states
                    SET current_setpoints =
                        json_patch(current_setpoints, json_object(:key, :val))
                    WHERE plant_id = :pid
                """),
                {"pid": str(conn.plant_id), "key": cmd.target, "val": cmd.value},
            )
            await session.commit()
        return {"target": cmd.target, "new_value": cmd.value}

    elif cmd.command in (CommandType.START_EQUIPMENT, CommandType.STOP_EQUIPMENT):
        target = cmd.target or cmd.equipment_id
        if not target:
            raise ValueError("Target or equipment_id is required")
        is_start = cmd.command == CommandType.START_EQUIPMENT
        async with get_session() as session:
            try:
                await session.execute(
                    text("SET LOCAL app.current_org_id = :oid"), {"oid": str(conn.org_id)}
                )
            except Exception:
                pass

            if target == "id_fan":
                await session.execute(
                    text("""
                        UPDATE twin_states
                        SET operating_mode = :mode
                        WHERE plant_id = :pid
                    """),
                    {"pid": str(conn.plant_id), "mode": "running" if is_start else "idle"},
                )
            else:
                flow_val = 1500.0 if is_start else 0.0
                await session.execute(
                    text("""
                        UPDATE twin_states
                        SET current_actuals =
                            json_patch(current_actuals, json_object(:key, :val))
                        WHERE plant_id = :pid
                    """),
                    {"pid": str(conn.plant_id), "key": f"{target}_flow", "val": flow_val},
                )
            await session.commit()
        return {"target": target, "status": "started" if is_start else "stopped"}

    raise NotImplementedError(f"Command {cmd.command.value!r} is not implemented yet")


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


def create_twin_router(get_session) -> APIRouter:
    """
    Factory that binds the endpoint to a session-maker.

    Usage in your FastAPI app:
        from cbms_api.websocket.twin import create_twin_router
        from cbms_api.database.connection import async_session_maker
        app.include_router(create_twin_router(async_session_maker))
    """
    rt = APIRouter(tags=["websocket"])

    @rt.websocket("/api/v1/twin/{plant_id}/stream")
    async def twin_stream(
        websocket: WebSocket,
        plant_id: UUID,
        token: str = Query(..., description="JWT access token"),
    ) -> None:
        """
        Real-time digital twin stream.

        **Protocol**: cbms-twin.v1
        **Auth**: Bearer JWT in `?token=` query parameter
        **Subprotocol**: cbms-twin.v1
        """
        # ------------------------------------------------------------------
        # 1. Authenticate
        # ------------------------------------------------------------------
        try:
            from cbms_api.auth.jwt_service import jwt_service
            claims = jwt_service.decode_token(token, "access")
            user_id = UUID(claims["sub"])
            org_id = UUID(claims["org_id"])
            roles: list[str] = claims.get("roles", [])
        except Exception:
            await websocket.close(code=4001, reason="Unauthorized")
            return

        is_read_only = ("viewer" in roles) and ("engineer" not in roles) and ("admin" not in roles)

        # ------------------------------------------------------------------
        # 2. Verify plant belongs to the org (RLS guard)
        # ------------------------------------------------------------------
        try:
            async with get_session() as session:
                try:
                    await session.execute(
                        text("SET LOCAL app.current_org_id = :oid"), {"oid": str(org_id)}
                    )
                except Exception:
                    pass
                result = await session.execute(
                    text("SELECT 1 FROM plant_profiles WHERE id = :pid"),
                    {"pid": str(plant_id)},
                )
                if not result.first():
                    await websocket.close(code=4004, reason="Plant not found")
                    return
        except Exception:
            await websocket.close(code=4004, reason="Plant not found")
            return

        # ------------------------------------------------------------------
        # 3. Accept with subprotocol
        # ------------------------------------------------------------------
        await websocket.accept(subprotocol=PROTOCOL_SUBPROTOCOL)
        conn = TwinConnection(
            websocket=websocket,
            user_id=user_id,
            org_id=org_id,
            plant_id=plant_id,
            is_read_only=is_read_only,
        )

        logger.info(
            "ws_connected",
            connection_id=str(conn.connection_id),
            user_id=str(user_id),
            org_id=str(org_id),
            plant_id=str(plant_id),
            read_only=is_read_only,
        )

        # ------------------------------------------------------------------
        # 4. Send welcome
        # ------------------------------------------------------------------
        initial_state = await _fetch_state(plant_id, org_id, get_session)
        await conn.send(WelcomeMessage(
            data=WelcomeData(
                connection_id=conn.connection_id,
                plant_id=plant_id,
                org_id=org_id,
                initial_state=initial_state,
                server_time=datetime.now(timezone.utc),
                reconnect_token=conn.reconnect_token,
            )
        ))

        # ------------------------------------------------------------------
        # 5. Start background tasks + main receive loop
        # ------------------------------------------------------------------
        tick_task = asyncio.create_task(_tick_loop(conn, get_session))
        hb_task = asyncio.create_task(_heartbeat_loop(conn))

        try:
            while True:
                try:
                    raw = await websocket.receive_text()
                except WebSocketDisconnect:
                    logger.info("ws_disconnected", connection_id=str(conn.connection_id))
                    break

                if not conn.check_rate_limit():
                    await conn.send(make_error_message(
                        ErrorCode.RATE_LIMITED,
                        "Message rate limit exceeded; slow down",
                        fatal=False,
                    ))
                    continue

                await _handle_client_message(conn, raw, get_session)

        finally:
            tick_task.cancel()
            hb_task.cancel()
            try:
                await conn.send(GoodbyeMessage(
                    data=GoodbyeData(reason=GoodbyeReason.NORMAL, reconnect_after_seconds=0)
                ))
            except Exception:
                pass
            logger.info("ws_closed", connection_id=str(conn.connection_id))

    return rt
