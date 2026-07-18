/**
 * packages/web/src/features/operator/pages/OperatorDashboard.tsx
 *
 * Route: /operator/live
 *
 * Full-screen DCS view:
 *   OperatorNav (fixed top)
 *   AlertBanner (sticky below nav)
 *   KPIStrip (6 tiles)
 *   [60%] PlantSchematic  [40%] AlarmList
 *   ActuatorDrawer (fixed bottom pull-up)
 *
 * Owns WS lifecycle via useTwinStream.
 */

import React, { useCallback, useRef } from "react";
import { useParams, Navigate } from "react-router-dom";
import { useTwinStream }     from "../../digital-twin/hooks/useTwinStream";
import { OperatorNav }       from "../components/OperatorNav";
import { AlertBanner }       from "../components/AlertBanner";
import { KPIStrip }          from "../components/KPIStrip";
import { PlantSchematic }    from "../components/PlantSchematic";
import { AlarmList }         from "../components/AlarmList";
import { ActuatorDrawer }    from "../components/ActuatorDrawer";
import { ReconnectionBanner } from "../../digital-twin/components/ReconnectionBanner";
import { derivePermissions } from "../types/operator";
import type { UserRole }     from "../types/operator";

// ---------------------------------------------------------------------------
// Skeleton
// ---------------------------------------------------------------------------

function OperatorSkeleton() {
  return (
    <div className="animate-pulse p-4 flex flex-col gap-3" aria-label="Loading…" role="status">
      <div className="h-14 rounded-xl bg-slate-800/60" />
      <div className="flex gap-2">
        {[...Array(6)].map((_, i) => <div key={i} className="flex-1 h-16 rounded-xl bg-slate-800/60" />)}
      </div>
      <div className="grid grid-cols-5 gap-3 flex-1">
        <div className="col-span-3 h-72 rounded-xl bg-slate-800/60" />
        <div className="col-span-2 h-72 rounded-xl bg-slate-800/60" />
      </div>
      <span className="sr-only">Loading live data…</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

interface OperatorDashboardProps {
  plantId: string;
  userRole?: UserRole;
}

function OperatorDashboard({ plantId, userRole = "operator" }: OperatorDashboardProps) {
  const permissions = derivePermissions(userRole);
  const alarmListRef = useRef<HTMLDivElement>(null);

  const {
    twinState, alerts, connectionState, reconnectAttempt, rttMs,
    sendCommand, acknowledgeAlert, reconnect,
  } = useTwinStream({ plantId });

  const alertsList = [...alerts.values()];

  const handleViewAlerts = useCallback(() => {
    alarmListRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const handleEscalate = useCallback(async (alertId: string) => {
    try {
      const res = await fetch(`/api/operator/escalate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          alert_id: alertId,
          plant_id: plantId,
        }),
      });
      if (!res.ok) {
        throw new Error(`Failed to escalate alert (Status ${res.status})`);
      }
      alert(`Alert ${alertId} has been successfully escalated to the on-call response team.`);
    } catch (err: any) {
      alert(err.message || "Failed to escalate alert.");
    }
  }, [plantId]);

  if (!twinState) return <OperatorSkeleton />;

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 text-slate-100">

      {/* Fixed top nav */}
      <OperatorNav
        plantId={plantId}
        alertCount={alertsList.length}
        connectionState={connectionState}
        rttMs={rttMs}
        onReconnect={reconnect}
      />

      {/* Scrollable body (offset for nav 48px) */}
      <div className="flex flex-col flex-1 overflow-y-auto mt-12">

        {/* Reconnection + Alert banners */}
        <ReconnectionBanner
          connectionState={connectionState}
          reconnectAttempt={reconnectAttempt}
          onRetry={reconnect}
        />
        <AlertBanner
          alerts={alertsList}
          onView={handleViewAlerts}
        />

        {/* KPI strip */}
        <KPIStrip state={twinState} />

        {/* Main content: schematic (60%) + alarm list (40%) */}
        <div className="flex-1 grid grid-cols-5 gap-3 px-4 pb-2 overflow-hidden">
          <div className="col-span-3 overflow-auto">
            <PlantSchematic state={twinState} />
          </div>
          <div ref={alarmListRef} className="col-span-2 overflow-auto">
            <AlarmList
              alerts={alerts}
              onAcknowledge={acknowledgeAlert}
              onEscalate={handleEscalate}
              canAcknowledge={permissions.canAcknowledge}
              canEscalate={permissions.canEscalate}
            />
          </div>
        </div>

        {/* Actuator drawer (docked bottom inside scroll) */}
        <ActuatorDrawer
          state={twinState}
          onCommand={sendCommand}
          canControl={permissions.canControl}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Route wrapper
// ---------------------------------------------------------------------------

export function OperatorDashboardPage() {
  const { plantId } = useParams<{ plantId?: string }>();

  // If no plantId in URL, use first available (placeholder)
  const resolvedPlantId = plantId ?? "default-plant";

  return <OperatorDashboard plantId={resolvedPlantId} />;
}
