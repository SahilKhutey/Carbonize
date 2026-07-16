/**
 * packages/web/src/features/operator/index.tsx
 * Operator DCS feature barrel.
 */
export { OperatorDashboardPage }   from "./pages/OperatorDashboard";
export { OperatorNav }             from "./components/OperatorNav";
export { AlertBanner }             from "./components/AlertBanner";
export { KPIStrip }                from "./components/KPIStrip";
export { PlantSchematic }          from "./components/PlantSchematic";
export { AlarmList }               from "./components/AlarmList";
export { ActuatorDrawer }          from "./components/ActuatorDrawer";
export { ConfirmDialog }           from "./components/ConfirmDialog";
export { derivePermissions, getDefaultRoute } from "./types/operator";
export type { UserRole, AuthUser, OperatorPermissions, AlarmHistoryEntry } from "./types/operator";
