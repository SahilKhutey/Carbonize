/**
 * packages/web/src/features/digital-twin/pages/TwinPage.tsx
 *
 * Route: /twin/:plantId
 *
 * Owns the WebSocket connection lifecycle via useTwinStream.
 * Renders TwinDashboard once state arrives; shows loading skeleton until then.
 */

import React, { Suspense } from "react";
import { useParams, Navigate } from "react-router-dom";
import { useTwinStream }      from "../hooks/useTwinStream";
import { useStateHistory }    from "../components/SensorTimeSeries";
import { TwinDashboard }      from "../components/TwinDashboard";
import { RefreshCw }          from "lucide-react";
import { DisconnectedBanner } from "../../../components/realtime/DisconnectedBanner";
import { ReconnectionToast }  from "../../../components/realtime/ReconnectionToast";
import { SkipLink, LiveRegion, useLiveAnnouncer } from "../../../components/a11y";

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function TwinSkeleton() {
  return (
    <div
      className="p-6 flex flex-col gap-4 animate-pulse"
      role="status"
      aria-label="Loading digital twin data"
    >
      {/* Header */}
      <div className="h-10 w-64 rounded-lg bg-slate-700/60" />
      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl bg-slate-700/60" />
        ))}
      </div>
      {/* Chart */}
      <div className="h-72 rounded-xl bg-slate-700/60" />
      {/* Two-col */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="h-48 rounded-xl bg-slate-700/60" />
        <div className="h-48 rounded-xl bg-slate-700/60" />
      </div>
      <span className="sr-only">Loading…</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error boundary
// ---------------------------------------------------------------------------

interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  return (
    <div
      className="p-8 flex flex-col items-center justify-center gap-4 text-center"
      role="alert"
    >
      <p className="text-red-400 font-semibold text-lg">{error}</p>
      <button
        onClick={onRetry}
        className="
          inline-flex items-center gap-2 px-4 py-2
          bg-emerald-700 hover:bg-emerald-600 text-white
          rounded-lg text-sm font-medium transition-colors
        "
      >
        <RefreshCw className="w-4 h-4" aria-hidden />
        Retry connection
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function TwinPage() {
  const { plantId } = useParams<{ plantId: string }>();

  // Guard: plantId must be present
  if (!plantId) return <Navigate to="/" replace />;

  const {
    twinState,
    alerts,
    connectionState,
    reconnectAttempt,
    rttMs,
    lastError,
    lastMessageAt,
    sendCommand,
    acknowledgeAlert,
    reconnect,
  } = useTwinStream({ plantId });

  const history = useStateHistory(twinState);
  const [dismissedDisconnect, setDismissedDisconnect] = React.useState(false);

  // Derive RBAC from auth context — placeholder (always engineer for now)
  const canControl = true;
  
  const { message, announce } = useLiveAnnouncer();
  
  // Announce connection state changes
  React.useEffect(() => {
    if (connectionState === "connected") announce("Connection restored", "polite");
    if (connectionState === "disconnected") announce("Connection lost", "assertive");
    if (connectionState === "connecting") announce("Reconnecting", "polite");
  }, [connectionState, announce]);

  const showDisconnectedBanner = connectionState !== "connected" && !dismissedDisconnect;

  if (lastError && !twinState) {
    return <ErrorDisplay error={lastError} onRetry={reconnect} />;
  }

  if (!twinState) {
    return <TwinSkeleton />;
  }

  return (
    <div className="flex flex-col min-h-screen">
      <SkipLink />
      <LiveRegion message={message} />
      {/* Persistent disconnection banner */}
      <DisconnectedBanner
        isVisible={showDisconnectedBanner}
        reconnectAttempt={reconnectAttempt}
        lastConnectedAt={lastMessageAt ?? undefined}
        onReconnect={reconnect}
        onDismiss={() => setDismissedDisconnect(true)}
        reason={lastError ?? undefined}
      />
      
      {/* Transient reconnection toast */}
      <ReconnectionToast
        state={connectionState}
        previousState="disconnected"
      />
      
      <main id="main-content" className="p-4 md:p-6 flex-1">
        <TwinDashboard
          state={twinState}
          history={history}
          alerts={alerts}
          connectionState={connectionState}
          reconnectAttempt={reconnectAttempt}
          lastMessageAt={lastMessageAt}
          rttMs={rttMs}
          canControl={canControl}
          plantId={plantId}
          onCommand={sendCommand}
          onAcknowledge={acknowledgeAlert}
          onReconnect={reconnect}
        />
      </main>
    </div>
  );
}
