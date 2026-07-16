/**
 * packages/web/src/features/digital-twin/components/ReconnectionBanner.tsx
 *
 * Full-width banner shown while the WebSocket is reconnecting.
 * Hides automatically once the connection is restored.
 */

import React, { memo } from "react";
import { RefreshCw, WifiOff } from "lucide-react";
import { ConnectionState } from "../types/twin";

interface ReconnectionBannerProps {
  connectionState: ConnectionState;
  reconnectAttempt: number;
  maxAttempts?: number;
  onRetry?: () => void;
}

export const ReconnectionBanner = memo(function ReconnectionBanner({
  connectionState,
  reconnectAttempt,
  maxAttempts = 10,
  onRetry,
}: ReconnectionBannerProps) {
  if (connectionState === "connected") return null;

  const isFailed =
    connectionState === "disconnected" && reconnectAttempt >= maxAttempts;
  const isReconnecting = connectionState === "reconnecting";
  const isConnecting = connectionState === "connecting";

  return (
    <div
      role="alert"
      className={`
        w-full px-4 py-2 flex items-center gap-3 text-sm font-medium
        ${isFailed
          ? "bg-red-900/80 text-red-200 border-b border-red-700"
          : "bg-amber-900/80 text-amber-200 border-b border-amber-700"
        }
      `}
    >
      {isFailed ? (
        <WifiOff className="w-4 h-4 shrink-0" aria-hidden />
      ) : (
        <RefreshCw className="w-4 h-4 shrink-0 animate-spin" aria-hidden />
      )}

      <span className="flex-1">
        {isFailed && "Connection lost — maximum retries exceeded."}
        {isReconnecting &&
          `Reconnecting to live data stream… (attempt ${reconnectAttempt} / ${maxAttempts})`}
        {isConnecting && "Connecting to live data stream…"}
        {connectionState === "disconnected" && !isFailed &&
          "Disconnected from live data stream."}
      </span>

      {(isFailed || connectionState === "disconnected") && onRetry && (
        <button
          onClick={onRetry}
          className="
            shrink-0 px-3 py-1 rounded border
            border-current hover:bg-white/10 transition-colors
            text-xs font-semibold
          "
          aria-label="Retry connection"
        >
          Retry
        </button>
      )}
    </div>
  );
});
