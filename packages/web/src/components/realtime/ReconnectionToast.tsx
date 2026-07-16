/**
 * Transient toast shown on connection state changes.
 * 
 * - "Connection lost" (red) → on disconnect
 * - "Reconnecting..." (amber) → on reconnecting
 * - "Connection restored" (green) → on reconnected
 */

import React, { useEffect, useState, useRef } from "react";
import { WifiOff, CheckCircle } from "lucide-react";
import { ConnectionState } from "@/hooks/useWebSocket";

interface ReconnectionToastProps {
  state: ConnectionState;
  previousState: ConnectionState;
  onDismiss?: () => void;
}

const TOAST_DURATION_MS = 5000;

export function ReconnectionToast({
  state, previousState, onDismiss,
}: ReconnectionToastProps) {
  const [visible, setVisible] = useState(false);
  const [toastType, setToastType] = useState<"lost" | "reconnected" | null>(null);
  const lastStateRef = useRef(previousState);
  
  useEffect(() => {
    // Detect transitions
    if (lastStateRef.current === "connected" && state === "disconnected") {
      setToastType("lost");
      setVisible(true);
    } else if (lastStateRef.current === "disconnected" && state === "connected") {
      setToastType("reconnected");
      setVisible(true);
    }
    lastStateRef.current = state;
    
    if (visible) {
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss?.();
      }, TOAST_DURATION_MS);
      return () => clearTimeout(timer);
    }
  }, [state, visible, onDismiss]);
  
  if (!visible || !toastType) return null;
  
  if (toastType === "lost") {
    return (
      <div className="fixed bottom-4 right-4 z-[100] animate-slide-in">
        <div className="bg-red-950 border border-red-800 rounded-lg shadow-xl p-4 max-w-sm">
          <div className="flex items-start gap-3">
            <WifiOff className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-100">
                Connection lost
              </p>
              <p className="text-xs text-red-400 mt-0.5">
                Attempting to reconnect automatically...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (toastType === "reconnected") {
    return (
      <div className="fixed bottom-4 right-4 z-[100] animate-slide-in">
        <div className="bg-emerald-950 border border-emerald-800 rounded-lg shadow-xl p-4 max-w-sm">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-emerald-500 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-emerald-100">
                Connection restored
              </p>
              <p className="text-xs text-emerald-400 mt-0.5">
                Real-time updates resumed
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return null;
}
