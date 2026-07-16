/**
 * packages/web/src/features/operator/types/operator.ts
 *
 * Operator DCS-specific types. Re-uses digital-twin protocol types.
 */

export type { TwinState, ConnectionState, SensorHistoryPoint } from "../../digital-twin/types/twin";
export type { AlertData, OperatingMode, CommandData } from "../../../types/ws";

/** User roles for RBAC */
export type UserRole =
  | "operator"
  | "engineer"
  | "admin"
  | "manager"
  | "investor"
  | "viewer";

/** Minimal auth user context */
export interface AuthUser {
  id: string;
  name: string;
  role: UserRole;
  org_id: string;
  assigned_plant_ids: string[];
}

/** Derived RBAC permissions */
export interface OperatorPermissions {
  canControl: boolean;    // start/stop actuators, change setpoints
  canAcknowledge: boolean;// acknowledge alarms
  canEscalate: boolean;   // escalate alarms to on-call
  canHandover: boolean;   // submit shift handover
}

export function derivePermissions(role: UserRole): OperatorPermissions {
  return {
    canControl:     role === "operator" || role === "engineer",
    canAcknowledge: role === "operator" || role === "engineer",
    canEscalate:    role === "operator" || role === "engineer" || role === "admin",
    canHandover:    role === "operator",
  };
}

/** Entry in the alarm history log */
export interface AlarmHistoryEntry {
  id: string;
  alert_id: string;
  severity: import("../../../types/ws").AlertSeverity;
  title: string;
  message: string;
  triggered_at: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_method: "acknowledged" | "auto_cleared" | "escalated";
}

/** Role → default route */
export function getDefaultRoute(role: UserRole): string {
  switch (role) {
    case "operator":
    case "engineer":
      return "/operator/live";
    default:
      return "/executive/dashboard";
  }
}
