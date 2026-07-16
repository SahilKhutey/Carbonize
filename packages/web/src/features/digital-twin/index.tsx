/**
 * packages/web/src/features/digital-twin/index.tsx
 *
 * Public barrel — import the Digital Twin feature from here.
 */

// Page (for router integration)
export { TwinPage } from "./pages/TwinPage";

// Components
export { TwinDashboard }          from "./components/TwinDashboard";
export { LiveKPIGrid }            from "./components/LiveKPIGrid";
export { SensorTimeSeries, useStateHistory } from "./components/SensorTimeSeries";
export { ActuatorGrid }           from "./components/ActuatorGrid";
export { AlertPanel }             from "./components/AlertPanel";
export { ConnectionStatus }       from "./components/ConnectionStatus";
export { OperatingModeIndicator } from "./components/OperatingModeIndicator";
export { ReconnectionBanner }     from "./components/ReconnectionBanner";

// Hook
export { useTwinStream }          from "./hooks/useTwinStream";

// Types
export type {
  TwinState,
  SensorHistoryPoint,
  ConnectionState,
  TwinSetpoints,
  TwinMaintenance,
} from "./types/twin";
