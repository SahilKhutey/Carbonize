/**
 * Full-width banner shown when disconnected.
 * Persistent (not toast) and impossible to ignore.
 * 
 * Appears at top of page, pushes content down.
 */

import React from "react";
import { WifiOff, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DisconnectedBannerProps {
  isVisible: boolean;
  reconnectAttempt: number;
  lastConnectedAt?: Date;
  onReconnect: () => void;
  onDismiss?: () => void;
  /** Optional detailed reason (e.g., "Auth expired", "Network unreachable") */
  reason?: string;
}

export function DisconnectedBanner({
  isVisible, reconnectAttempt, lastConnectedAt, onReconnect, onDismiss, reason,
}: DisconnectedBannerProps) {
  if (!isVisible) return null;
  
  const downtimeSeconds = lastConnectedAt
    ? Math.floor((Date.now() - lastConnectedAt.getTime()) / 1000)
    : null;
  
  return (
    <div className="sticky top-0 z-40 bg-red-950 border-b-2 border-red-800 shadow-md animate-slide-down">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="flex-shrink-0">
            <div className="bg-red-900 rounded-full p-2">
              <WifiOff className="w-5 h-5 text-red-400" />
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-red-100">
              Real-time connection lost
            </p>
            <p className="text-xs text-red-300">
              {reason ?? "Displaying cached data. "}
              {reconnectAttempt > 0 && (
                <span>Reconnect attempt #{reconnectAttempt}. </span>
              )}
              {downtimeSeconds !== null && downtimeSeconds > 0 && (
                <span>Downtime: {downtimeSeconds}s.</span>
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={onReconnect}
            className="border-red-700 text-red-400 hover:bg-red-900"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Retry now
          </Button>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-xs text-red-500 hover:text-red-300 ml-2"
              aria-label="Dismiss"
            >
              ✕
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
