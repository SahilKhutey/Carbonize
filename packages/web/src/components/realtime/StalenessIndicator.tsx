/**
 * "As of Xs ago" label for data freshness.
 * 
 * Always shown on real-time data so user knows how fresh it is.
 */

import React, { useEffect, useState } from "react";
import { Clock } from "lucide-react";

interface StalenessIndicatorProps {
  /** When the data was last received */
  lastUpdateAt: Date;
  /** Threshold (seconds) after which data is considered "stale" (default 10) */
  staleThresholdSeconds?: number;
  /** Whether to show even when fresh (default true) */
  alwaysShow?: boolean;
  /** Compact mode (no icon, just text) */
  compact?: boolean;
}

export function StalenessIndicator({
  lastUpdateAt,
  staleThresholdSeconds = 10,
  alwaysShow = true,
  compact = false,
}: StalenessIndicatorProps) {
  const [now, setNow] = useState(Date.now());
  
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);
  
  const ageSeconds = Math.max(0, Math.floor((now - lastUpdateAt.getTime()) / 1000));
  const isStale = ageSeconds > staleThresholdSeconds;
  
  if (!alwaysShow && !isStale) return null;
  
  let colorClass;
  if (ageSeconds < 5) {
    colorClass = "text-emerald-600";
  } else if (ageSeconds < 30) {
    colorClass = "text-gray-500";
  } else if (ageSeconds < 60) {
    colorClass = "text-amber-600";
  } else {
    colorClass = "text-red-600 font-semibold";
  }
  
  const formatAge = (s: number) => {
    if (s < 60) return `${s}s ago`;
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    return `${Math.floor(s / 3600)}h ago`;
  };
  
  return (
    <span className={`inline-flex items-center gap-0.5 text-[10px] tabular-nums ${colorClass}`}>
      {!compact && <Clock className="w-2.5 h-2.5" />}
      {formatAge(ageSeconds)}
    </span>
  );
}
