/**
 * packages/web/src/features/operator/components/AlertBanner.tsx
 *
 * Sticky alert banner shown below the nav when any alerts are active.
 * Highest visual priority signal on the operator dashboard.
 */

import React, { memo } from "react";
import { AlertTriangle, X } from "lucide-react";
import type { AlertData } from "../../../types/ws";

interface AlertBannerProps {
  alerts: AlertData[];
  onView?: () => void;
  onDismiss?: () => void;
}

export const AlertBanner = memo(function AlertBanner({
  alerts,
  onView,
  onDismiss,
}: AlertBannerProps) {
  if (alerts.length === 0) return null;

  const criticals = alerts.filter((a) => a.severity === "CRITICAL");
  const first = criticals[0] ?? alerts[0];
  const hasCritical = criticals.length > 0;

  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className={`
        w-full px-4 py-2.5
        flex items-center gap-3
        text-sm font-medium
        ${hasCritical
          ? "bg-red-900/90 border-b-2 border-red-500 text-red-100"
          : "bg-amber-900/90 border-b-2 border-amber-500 text-amber-100"
        }
      `}
    >
      <AlertTriangle
        className={`w-5 h-5 shrink-0 ${hasCritical ? "text-red-400" : "text-amber-400"}`}
        aria-hidden
      />

      <span className="flex-1 min-w-0">
        <span className="font-bold">
          {alerts.length} ALERT{alerts.length !== 1 ? "S" : ""}
        </span>
        {hasCritical && (
          <span className="ml-2">
            • {criticals.length} CRITICAL: &ldquo;{first.title}&rdquo;
          </span>
        )}
        {!hasCritical && (
          <span className="ml-2">• &ldquo;{first.title}&rdquo;</span>
        )}
      </span>

      {onView && (
        <button
          onClick={onView}
          className="
            shrink-0 px-3 py-1 rounded border border-current
            hover:bg-white/10 transition-colors text-xs font-bold uppercase
            min-h-[44px] min-w-[64px]
          "
          aria-label="View all alerts"
        >
          View ▸
        </button>
      )}

      {onDismiss && (
        <button
          onClick={onDismiss}
          className="shrink-0 p-1.5 rounded hover:bg-white/10 transition-colors"
          aria-label="Dismiss alert banner"
        >
          <X className="w-4 h-4" aria-hidden />
        </button>
      )}
    </div>
  );
});
