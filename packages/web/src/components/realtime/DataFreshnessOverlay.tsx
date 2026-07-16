/**
 * Wraps any chart with a staleness overlay.
 * 
 * When data is "stale" (no update for N seconds), the chart dims
 * and shows a "stale" badge. This makes it OBVIOUS to the user
 * that the data isn't live.
 */

import React, { useEffect, useState } from "react";
import { AlertTriangle, EyeOff } from "lucide-react";

interface DataFreshnessOverlayProps {
  /** Last time data was received (Date or null) */
  lastUpdateAt: Date | null;
  /** Children: the actual chart component */
  children: React.ReactNode;
  /** After this many seconds, mark data as "stale" */
  staleThresholdSeconds?: number;
  /** After this many seconds, mark data as "very stale" (further dim) */
  veryStaleThresholdSeconds?: number;
  /** Show the staleness banner */
  showBanner?: boolean;
}

export function DataFreshnessOverlay({
  lastUpdateAt,
  children,
  staleThresholdSeconds = 10,
  veryStaleThresholdSeconds = 60,
  showBanner = true,
}: DataFreshnessOverlayProps) {
  const [now, setNow] = useState(Date.now());
  
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);
  
  // No data ever received
  if (!lastUpdateAt) {
    return (
      <div className="relative">
        <div className="opacity-30 pointer-events-none">{children}</div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-lg p-6 text-center">
            <EyeOff className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-sm text-slate-400">No data received yet</p>
            <p className="text-xs text-slate-500 mt-1">Waiting for first update...</p>
          </div>
        </div>
      </div>
    );
  }
  
  const ageSeconds = Math.floor((now - lastUpdateAt.getTime()) / 1000);
  const isStale = ageSeconds >= staleThresholdSeconds;
  const isVeryStale = ageSeconds >= veryStaleThresholdSeconds;
  
  return (
    <div className="relative">
      {/* The chart, with opacity reduced when stale */}
      <div
        className={`
          transition-opacity duration-500
          ${isStale ? "opacity-70" : "opacity-100"}
          ${isVeryStale ? "opacity-50 grayscale" : ""}
        `}
      >
        {children}
      </div>
      
      {/* Stale banner */}
      {showBanner && isStale && (
        <div className="absolute top-2 left-2 right-2 z-10 flex justify-center">
          <div className={`
            inline-flex items-center gap-2 px-2 py-1 rounded
            text-xs font-medium shadow-md
            ${isVeryStale 
              ? "bg-red-950 text-red-400 border border-red-800" 
              : "bg-amber-950 text-amber-400 border border-amber-800"}
          `}>
            <AlertTriangle className="w-3 h-3" />
            <span>
              {isVeryStale ? "VERY" : ""} STALE DATA · {ageSeconds}s
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
