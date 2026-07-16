/**
 * packages/web/src/features/digital-twin/types/twin.ts
 *
 * Domain types for the Digital Twin feature.
 * Re-uses the generated WS protocol types from src/types/ws.ts and
 * adds UI-centric composites.
 */

// Re-export the WS protocol types we use directly
export type {
  AlertSeverity,
  OperatingMode,
  CommandType,
  CommandAckStatus,
  GoodbyeReason,
  ActualsData as TwinSensorReadings,
  PerformanceData as TwinPerformance,
  AlertData,
  TickData,
  WelcomeData,
  CommandData,
  CommandAckData,
} from "../../../types/ws";

// -----------------------------------------------------------------
// UI-level composites (not in the wire protocol)
// -----------------------------------------------------------------

export interface TwinSetpoints {
  reactor_temp_c?: number | null;
  pH?: number | null;
  liquid_to_gas_ratio?: number | null;
  [key: string]: number | null | undefined;
}

export interface TwinMaintenance {
  type: string;
  predicted_at: string;
  severity?: "info" | "warning" | "critical";
}

/** Flat state object hydrated from welcome + tick messages */
export interface TwinState {
  plant_id: string;
  org_id: string;
  operating_mode: import("../../../types/ws").OperatingMode;
  current_actuals: import("../../../types/ws").ActualsData;
  current_setpoints: TwinSetpoints;
  performance: import("../../../types/ws").PerformanceData;
  next_maintenance?: TwinMaintenance | null;
  active_alerts: import("../../../types/ws").AlertData[];
  uptime_seconds: number;
  last_update: string;
}

/** History point accumulated by useStateHistory */
export interface SensorHistoryPoint {
  timestamp: number;
  readings: import("../../../types/ws").ActualsData;
}

/** Connection state for the UI */
export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting";
