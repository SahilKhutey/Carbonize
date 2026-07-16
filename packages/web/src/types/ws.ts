/**
 * packages/web/src/types/ws.ts
 *
 * WebSocket protocol types for the CBMS-Sim digital twin real-time stream.
 *
 * AUTO-GENERATED from Pydantic models in:
 *   packages/api/src/cbms_api/websocket/v1_models.py
 *
 * Do NOT edit manually. To regenerate:
 *   python scripts/generate_ws_schema.py > docs/architecture/ws-schema.json
 *   pnpm run generate:ws-types
 */

// ---------------------------------------------------------------------------
// Protocol constants
// ---------------------------------------------------------------------------

export const PROTOCOL_VERSION = "1.0" as const;
export const PROTOCOL_SUBPROTOCOL = "cbms-twin.v1" as const;

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export type AlertSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type CommandType =
  | "set_setpoint"
  | "start_equipment"
  | "stop_equipment"
  | "acknowledge_alert";

export type CommandAckStatus = "success" | "rejected" | "error";

export type GoodbyeReason =
  | "server_shutdown"
  | "auth_expired"
  | "rate_limited"
  | "normal"
  | "unauthorized";

export type OperatingMode =
  | "idle"
  | "starting"
  | "running"
  | "stopping"
  | "fault"
  | "maintenance";

export type ErrorCode =
  | "INVALID_MESSAGE"
  | "UNKNOWN_TYPE"
  | "RATE_LIMITED"
  | "AUTH_EXPIRED"
  | "FORBIDDEN"
  | "INVALID_COMMAND"
  | "INTERNAL_ERROR";

// ---------------------------------------------------------------------------
// Message envelope
// ---------------------------------------------------------------------------

export interface MessageEnvelope<TData = unknown> {
  /** Message type discriminator */
  type: string;
  /** Protocol version — "major.minor" */
  version: string;
  /** Unique message ID (UUID) — use for deduplication */
  id: string;
  /** Sender UTC timestamp (ISO 8601) */
  ts: string;
  /** Per-connection monotonic sequence number (starts at 1) */
  seq: number;
  /** Type-specific payload */
  data: TData;
}

// ---------------------------------------------------------------------------
// Data payloads
// ---------------------------------------------------------------------------

export interface WelcomeData {
  /** Server-assigned connection UUID */
  connection_id: string;
  plant_id: string;
  org_id: string;
  /** Current TwinState snapshot */
  initial_state: Record<string, unknown>;
  /** Server clock for client synchronisation */
  server_time: string;
  /** Opaque token for session resumption */
  reconnect_token: string;
  /** Default tick interval in seconds */
  tick_interval_seconds: number;
}

export interface SubscribeData {
  tick_interval_seconds?: number;
  include_alerts?: boolean;
  include_predictions?: boolean;
  /** Last received seq number; null for fresh connections */
  resume_from_seq?: number | null;
  reconnect_token?: string | null;
}

export interface ActualsData {
  co2_inlet_pct?: number | null;
  co2_outlet_pct?: number | null;
  so2_inlet_mg_nm3?: number | null;
  so2_outlet_mg_nm3?: number | null;
  mesh_dp_mmH2O?: number | null;
  reactor_temp_c?: number | null;
  [key: string]: number | null | undefined; // forward-compat
}

export interface PerformanceData {
  co2_capture_pct?: number | null;
  so2_capture_pct?: number | null;
  energy_consumption_kw?: number | null;
  [key: string]: number | null | undefined;
}

export interface MaintenancePrediction {
  type: string;
  predicted_at: string;
  [key: string]: unknown;
}

export interface TickData {
  operating_mode: OperatingMode;
  current_actuals: ActualsData;
  current_setpoints: Record<string, unknown>;
  performance: PerformanceData;
  next_maintenance?: MaintenancePrediction | null;
  uptime_seconds: number;
}

export interface AlertData {
  alert_id: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  metric?: string | null;
  value?: number | null;
  threshold?: number | null;
  triggered_at: string;
  recommended_action?: string | null;
}

export interface AlertClearedData {
  alert_id: string;
  cleared_at: string;
  auto_resolved: boolean;
}

export interface CommandData {
  command: CommandType;
  target?: string | null;
  value?: number | string | boolean | null;
  equipment_id?: string | null;
  alert_id?: string | null;
  reason?: string | null;
}

export interface CommandAckData {
  /** Echoes the originating client message ID */
  command_id: string;
  status: CommandAckStatus;
  error?: string | null;
  new_state?: Record<string, unknown> | null;
}

export interface PingData {
  client_ts?: string | null;
}

export interface PongData {
  client_ts?: string | null;
  /** Round-trip time in milliseconds */
  rtt_ms?: number | null;
}

export interface ErrorData {
  code: ErrorCode;
  message: string;
  /** If true, client should NOT attempt reconnect */
  fatal: boolean;
}

export interface GoodbyeData {
  reason: GoodbyeReason;
  reconnect_after_seconds: number;
  message?: string | null;
}

export interface ResumeData {
  /** Last sequence number the client received before disconnect */
  from_seq: number;
  /** Reconnect token from the welcome message */
  reconnect_token: string;
}

// ---------------------------------------------------------------------------
// Typed message wrappers
// ---------------------------------------------------------------------------

export type WelcomeMessage = MessageEnvelope<WelcomeData> & { type: "welcome" };
export type SubscribeMessage = MessageEnvelope<SubscribeData> & { type: "subscribe" };
export type TickMessage = MessageEnvelope<TickData> & { type: "tick" };
export type AlertMessage = MessageEnvelope<AlertData> & { type: "alert" };
export type AlertClearedMessage = MessageEnvelope<AlertClearedData> & { type: "alert_cleared" };
export type CommandMessage = MessageEnvelope<CommandData> & { type: "command" };
export type CommandAckMessage = MessageEnvelope<CommandAckData> & { type: "command_ack" };
export type PingMessage = MessageEnvelope<PingData> & { type: "ping" };
export type PongMessage = MessageEnvelope<PongData> & { type: "pong" };
export type ErrorMessage = MessageEnvelope<ErrorData> & { type: "error" };
export type GoodbyeMessage = MessageEnvelope<GoodbyeData> & { type: "goodbye" };
export type ResumeMessage = MessageEnvelope<ResumeData> & { type: "resume" };

// Discriminated union of every message on the wire
export type WSMessage =
  | WelcomeMessage
  | SubscribeMessage
  | TickMessage
  | AlertMessage
  | AlertClearedMessage
  | CommandMessage
  | CommandAckMessage
  | PingMessage
  | PongMessage
  | ErrorMessage
  | GoodbyeMessage
  | ResumeMessage;

// Directional sub-types
export type ServerMessage =
  | WelcomeMessage
  | TickMessage
  | AlertMessage
  | AlertClearedMessage
  | CommandAckMessage
  | PongMessage
  | ErrorMessage
  | GoodbyeMessage;

export type ClientMessage =
  | SubscribeMessage
  | CommandMessage
  | PingMessage
  | ResumeMessage;

// ---------------------------------------------------------------------------
// Type guard helpers
// ---------------------------------------------------------------------------

export function isWelcome(m: WSMessage): m is WelcomeMessage   { return m.type === "welcome"; }
export function isTick(m: WSMessage): m is TickMessage         { return m.type === "tick"; }
export function isAlert(m: WSMessage): m is AlertMessage       { return m.type === "alert"; }
export function isAlertCleared(m: WSMessage): m is AlertClearedMessage { return m.type === "alert_cleared"; }
export function isCommandAck(m: WSMessage): m is CommandAckMessage     { return m.type === "command_ack"; }
export function isPong(m: WSMessage): m is PongMessage         { return m.type === "pong"; }
export function isError(m: WSMessage): m is ErrorMessage       { return m.type === "error"; }
export function isGoodbye(m: WSMessage): m is GoodbyeMessage   { return m.type === "goodbye"; }
