/**
 * packages/web/src/features/digital-twin/components/ConnectionStatus.tsx
 *
 * Pill indicator for WebSocket connection state.
 * Shows live RTT when connected; a "Retry" button when disconnected.
 */

import React, { memo } from "react";
import { Wifi, WifiOff, RefreshCw } from "lucide-react";
import { ConnectionState } from "../types/twin";

interface ConnectionStatusProps {
  state: ConnectionState;
  reconnectAttempt?: number;
  rttMs?: number | null;
  onReconnect?: () => void;
}

const CONFIG = {
  disconnected: {
    icon: <WifiOff className="w-3.5 h-3.5" />,
    label: "Disconnected",
    classes: "bg-red-900/60 border-red-700 text-red-300",
  },
  connecting: {
    icon: <RefreshCw className="w-3.5 h-3.5 animate-spin" />,
    label: "Connecting…",
    classes: "bg-amber-900/60 border-amber-700 text-amber-300",
  },
  connected: {
    icon: <Wifi className="w-3.5 h-3.5" />,
    label: "Live",
    classes: "bg-emerald-900/60 border-emerald-700 text-emerald-300",
  },
  reconnecting: {
    icon: <RefreshCw className="w-3.5 h-3.5 animate-spin" />,
    label: "Reconnecting…",
    classes: "bg-amber-900/60 border-amber-700 text-amber-300",
  },
} as const;

export const ConnectionStatus = memo(function ConnectionStatus({
  state,
  reconnectAttempt = 0,
  rttMs,
  onReconnect,
}: ConnectionStatusProps) {
  const { icon, label, classes } = CONFIG[state];

  return (
    <div
      role="status"
      aria-label={`WebSocket: ${label}`}
      className={`
        inline-flex items-center gap-1.5 px-3 py-1 rounded-full
        border text-xs font-medium select-none
        ${classes}
      `}
    >
      {icon}
      <span>{label}</span>

      {state === "reconnecting" && reconnectAttempt > 0 && (
        <span className="text-amber-500">({reconnectAttempt})</span>
      )}

      {state === "connected" && rttMs != null && (
        <span className="text-emerald-500 ml-0.5">{rttMs.toFixed(0)} ms</span>
      )}

      {state === "disconnected" && onReconnect && (
        <button
          onClick={onReconnect}
          className="ml-1 underline text-red-400 hover:text-red-200 transition-colors"
          aria-label="Retry connection"
        >
          Retry
        </button>
      )}
    </div>
  );
});
