# CBMS-Sim WebSocket Protocol — Digital Twin Real-Time

**Version**: 1.0  
**Status**: Approved  
**Location**: `docs/architecture/websocket-protocol.md`

---

## Overview

The CBMS-Sim digital twin feature streams real-time sensor data, control commands, and alerts over WebSocket.

| Property | Value |
|---|---|
| **Endpoint** | `wss://api.cbms.in/api/v1/twin/{plant_id}/stream` |
| **Transport** | WebSocket over TLS (WSS required in production) |
| **Auth** | `?token=<JWT access token>` query parameter |
| **Subprotocol** | `cbms-twin.v1` |
| **Direction** | Bidirectional (server pushes; client sends commands) |

---

## Connection Lifecycle

```
Client                                Server
  |                                      |
  |── HTTP/1.1 Upgrade (token) ─────────►|
  |◄── 101 Switching Protocols ──────────|
  |                                      |
  |◄── {"type":"welcome", ...} ──────────|  (server hello, seq=1)
  |── {"type":"subscribe", ...} ─────────►|  (client ack)
  |                                      |
  |◄── {"type":"tick", ...} (every 5s) ──|  (state updates)
  |◄── {"type":"alert", ...} (when) ─────|  (alerts)
  |◄── {"type":"pong", ...} ─────────────|  (heartbeat responses)
  |                                      |
  |── {"type":"command", ...} ───────────►|  (operator action)
  |◄── {"type":"command_ack", ...} ──────|  (server confirms)
  |── {"type":"ping"} ───────────────────►|  (keepalive)
  |◄── {"type":"pong"} ─────────────────|
```

---

## Message Envelope

All messages share this structure:

```json
{
  "type":    "<string>",    // required — message type discriminator
  "version": "1.0",         // required — protocol version
  "id":      "<uuid>",      // required — unique per message (use for dedup)
  "ts":      "<iso8601>",   // required — UTC timestamp from sender
  "seq":     42,            // required — monotonic per-connection sequence
  "data":    { ... }        // required — type-specific payload
}
```

---

## Message Types

### Server → Client

| Type | When | Description |
|---|---|---|
| `welcome` | On connect (seq=1) | Server hello, initial state snapshot, reconnect_token |
| `tick` | Every N seconds | Current sensor actuals, setpoints, and performance |
| `alert` | Alert triggered | Alert details with severity and recommended action |
| `alert_cleared` | Alert resolved | Alert cleared (auto or manual) |
| `command_ack` | After client command | Success/rejected/error with optional new_state |
| `pong` | After ping | Echoes client_ts for RTT calculation |
| `error` | Protocol error | Error code + message + fatal flag |
| `goodbye` | Before server close | Reason + reconnect_after_seconds |

### Client → Server

| Type | When | Description |
|---|---|---|
| `subscribe` | After `welcome` | Confirm subscription, set tick interval, resume |
| `command` | Operator action | set_setpoint, start/stop_equipment, acknowledge_alert |
| `ping` | Every 30s | Keepalive; echoed as `pong` |
| `resume` | On reconnect | Request replay of messages since `from_seq` |

---

## Key Payloads

### `welcome.data`
```json
{
  "connection_id": "uuid",
  "plant_id": "uuid",
  "org_id": "uuid",
  "initial_state": { "operating_mode": "running", "current_actuals": { ... } },
  "server_time": "2026-01-01T00:00:00Z",
  "reconnect_token": "opaque-32+-char-string",
  "tick_interval_seconds": 5
}
```

### `tick.data`
```json
{
  "operating_mode": "running",
  "current_actuals": {
    "co2_inlet_pct": 14.1,
    "co2_outlet_pct": 1.8,
    "so2_inlet_mg_nm3": 1200,
    "so2_outlet_mg_nm3": 38,
    "reactor_temp_c": 40.2
  },
  "current_setpoints": { "reactor_temp_c": 40.0 },
  "performance": { "co2_capture_pct": 87.2, "so2_capture_pct": 96.8 },
  "uptime_seconds": 3600
}
```

### `command.data` (set setpoint)
```json
{
  "command": "set_setpoint",
  "target": "reactor_temp_c",
  "value": 42.0,
  "reason": "operator_action"
}
```

### `alert.data`
```json
{
  "alert_id": "uuid",
  "severity": "HIGH",
  "title": "SO₂ outlet spike",
  "message": "Outlet SO₂ at 245 mg/Nm³ exceeds threshold of 200",
  "metric": "so2_outlet_mg_nm3",
  "value": 245,
  "threshold": 200,
  "triggered_at": "...",
  "recommended_action": "Increase L/G ratio"
}
```

---

## Versioning

| Change | Rule |
|---|---|
| New **field** (same type) | Additive — old clients safe (extra ignored) |
| New **message type** | Additive — old clients ignore unknown types |
| **Removed** field or changed semantics | Breaking → bump major (1.x → 2.0) |

- Clients **must** include `version`
- Clients **must** ignore messages with unknown `type` (forward-compat)
- Server **rejects** messages with `major > server_major`

---

## Reconnection Strategy

| Attempt | Delay |
|---|---|
| 1 | 0 s (immediate) |
| 2 | 1 s + jitter |
| 3 | 2 s + jitter |
| 4 | 4 s + jitter |
| 5 | 8 s + jitter |
| 6+ | 16 s / 30 s cap + jitter |
| > 10 | Give up, surface error to user |

Jitter: `random(0, 1000) ms` added to each delay.

### Session Resumption

1. Server sends `welcome.data.reconnect_token` on connect
2. Client stores `reconnect_token` and tracks `lastSeq`
3. On reconnect, client sends `subscribe` with `resume_from_seq` + `reconnect_token`
4. Server replays buffered messages with `seq > from_seq` (up to 1,000)
5. If too many missed: server sends fresh `welcome` with current state

---

## Security

| Control | Detail |
|---|---|
| **Transport** | WSS (TLS) required in production |
| **Auth** | Full JWT validated on connection |
| **Tenant isolation** | `org_id` extracted from JWT; all DB queries RLS-scoped |
| **Read-only roles** | `viewer` role receives ticks/alerts but `command` messages are rejected |
| **Rate limiting** | 60 messages/min per connection |
| **Connection limit** | Max 3 connections per user |

---

## Performance Targets

| Metric | Target |
|---|---|
| Server push latency (sensor → client) | < 2 s p95 |
| Client-to-server round trip | < 100 ms p95 |
| Server CPU per connection | < 1 % |
| Max concurrent connections | 10,000 per server node |

---

## Error Codes

| Code | Meaning |
|---|---|
| `INVALID_MESSAGE` | Malformed JSON or missing required fields |
| `UNKNOWN_TYPE` | Message type not in this protocol version |
| `RATE_LIMITED` | Too many messages in the rate window |
| `AUTH_EXPIRED` | JWT no longer valid; reconnect with fresh token |
| `FORBIDDEN` | Insufficient permission (e.g., viewer sending command) |
| `INVALID_COMMAND` | Command target or value invalid |
| `INTERNAL_ERROR` | Server error; safe to retry |

---

## Source of Truth & Codegen

```
packages/api/src/cbms_api/websocket/v1_models.py  ← Pydantic v2 (EDIT HERE)
        │
        ▼
scripts/generate_ws_schema.py                      ← generates ↓
        │
        ▼
docs/architecture/ws-schema.json                   ← JSON Schema
        │
        ▼
packages/web/src/types/ws.ts                       ← TypeScript types (via codegen)
```

### Regeneration commands
```bash
# Step 1: regenerate JSON Schema
python scripts/generate_ws_schema.py > docs/architecture/ws-schema.json

# Step 2: regenerate TypeScript types (optional — types/ws.ts maintained manually for now)
# npx json-schema-to-typescript docs/architecture/ws-schema.json \
#     --out packages/web/src/types/ws-generated.d.ts
```

---

## Files

| File | Purpose |
|---|---|
| [`v1_models.py`](file:///c:/Users/ASUS/Documents/Carbonize/packages/api/src/cbms_api/websocket/v1_models.py) | Pydantic models (source of truth) |
| [`twin.py`](file:///c:/Users/ASUS/Documents/Carbonize/packages/api/src/cbms_api/websocket/twin.py) | FastAPI WebSocket endpoint |
| [`ws.ts`](file:///c:/Users/ASUS/Documents/Carbonize/packages/web/src/types/ws.ts) | TypeScript types |
| [`wsClient.ts`](file:///c:/Users/ASUS/Documents/Carbonize/packages/web/src/lib/wsClient.ts) | Frontend WebSocket client |
| [`generate_ws_schema.py`](file:///c:/Users/ASUS/Documents/Carbonize/scripts/generate_ws_schema.py) | JSON Schema codegen script |
| [`test_ws_protocol.py`](file:///c:/Users/ASUS/Documents/Carbonize/packages/api/tests/contract/test_ws_protocol.py) | Contract tests |
