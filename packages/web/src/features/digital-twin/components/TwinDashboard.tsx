/**
 * packages/web/src/features/digital-twin/components/TwinDashboard.tsx
 *
 * Main container component that assembles all sub-panels.
 * Accepts fully-resolved props (no WebSocket awareness here).
 */

import React, { memo } from "react";
import { AlertData } from "../../../types/ws";
import { TwinState, ConnectionState, SensorHistoryPoint } from "../types/twin";
import { CommandData } from "../../../types/ws";

import { LiveKPIGrid }           from "./LiveKPIGrid";
import { SensorTimeSeries }      from "./SensorTimeSeries";
import { ActuatorGrid }          from "./ActuatorGrid";
import { AlertPanel }            from "./AlertPanel";
import { ConnectionStateIndicator } from "../../../components/realtime/ConnectionStateIndicator";
import { DataFreshnessOverlay }  from "../../../components/realtime/DataFreshnessOverlay";
import { OperatingModeIndicator } from "./OperatingModeIndicator";
import { ModbusRegisterMapInspector } from "./ModbusRegisterMapInspector";
import { PredictiveDriftOverlay }     from "./PredictiveDriftOverlay";
import { formatUptime }          from "../utils/formatters";

interface TwinDashboardProps {
  state: TwinState;
  history: SensorHistoryPoint[];
  alerts: Map<string, AlertData>;
  connectionState: ConnectionState;
  reconnectAttempt: number;
  lastMessageAt: Date | null;
  rttMs: number | null;
  canControl: boolean;
  plantId: string;
  onCommand: (cmd: CommandData) => boolean;
  onAcknowledge: (alertId: string) => void;
  onReconnect: () => void;
}

export const TwinDashboard = memo(function TwinDashboard({
  state,
  history,
  alerts,
  connectionState,
  reconnectAttempt,
  lastMessageAt,
  rttMs,
  canControl,
  plantId,
  onCommand,
  onAcknowledge,
  onReconnect,
}: TwinDashboardProps) {
  return (
    <div className="flex flex-col gap-4 max-w-[1800px] mx-auto">
      {/* ---------------------------------------------------------------- */}
      {/* Header row                                                         */}
      {/* ---------------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">
            Digital Twin
            <span className="ml-2 text-sm font-mono text-slate-500">
              #{plantId.slice(0, 8)}
            </span>
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <OperatingModeIndicator mode={state.operating_mode} />
            <span className="text-xs text-slate-500">
              Uptime: {formatUptime(state.uptime_seconds)}
            </span>
          </div>
        </div>

        <ConnectionStateIndicator
          state={connectionState}
          reconnectAttempt={reconnectAttempt}
          lastUpdateAt={lastMessageAt ?? undefined}
          onClick={onReconnect}
        />
      </div>

      {/* ---------------------------------------------------------------- */}
      {/* Real-time Predictive Physics Drift Overlay                        */}
      {/* ---------------------------------------------------------------- */}
      <PredictiveDriftOverlay state={state} />

      {/* ---------------------------------------------------------------- */}
      {/* KPI tiles                                                          */}
      {/* ---------------------------------------------------------------- */}
      <DataFreshnessOverlay
        lastUpdateAt={lastMessageAt}
        staleThresholdSeconds={10}
        veryStaleThresholdSeconds={60}
      >
        <LiveKPIGrid state={state} />
      </DataFreshnessOverlay>

      {/* ---------------------------------------------------------------- */}
      {/* Main content: chart + (actuators + alerts)                       */}
      {/* ---------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main: chart (2/3 on desktop) */}
        <div className="lg:col-span-2 order-1 space-y-4">
          <DataFreshnessOverlay
            lastUpdateAt={lastMessageAt}
            staleThresholdSeconds={10}
            veryStaleThresholdSeconds={60}
          >
            <div className="w-full h-[300px] sm:h-[350px] md:h-[400px] lg:h-[350px] xl:h-[400px]">
              <SensorTimeSeries
                history={history}
                metrics={["co2_outlet_pct", "so2_outlet_mg_nm3", "mesh_dp_mmH2O", "reactor_temp_c"]}
                title="Sensor Trends"
              />
            </div>
          </DataFreshnessOverlay>

          {/* Siemens S7-1200 / NI cDAQ Modbus Register Map Inspector */}
          <ModbusRegisterMapInspector state={state} />
        </div>

        {/* Side: actuators + alerts (1/3 on desktop) */}
        <aside 
          className="lg:col-span-1 order-2 space-y-4"
          aria-label="Alerts and controls"
        >
          <ActuatorGrid
            state={state}
            onCommand={onCommand}
            canControl={canControl}
          />
          <AlertPanel
            alerts={alerts}
            onAcknowledge={onAcknowledge}
          />
        </aside>
      </div>
    </div>
  );
});
