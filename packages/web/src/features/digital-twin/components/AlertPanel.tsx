/**
 * packages/web/src/features/digital-twin/components/AlertPanel.tsx
 *
 * Live alert feed with severity sorting and acknowledge capability.
 */

import React, { memo, useState, useCallback } from "react";
import { AlertTriangle, AlertCircle, Info, Check, Bell } from "lucide-react";
import { AlertData, AlertSeverity } from "../../../types/ws";
import { formatTime } from "../utils/formatters";

// ---------------------------------------------------------------------------
// Severity config
// ---------------------------------------------------------------------------

const SEV: Record<AlertSeverity, { icon: React.ReactNode; border: string; bg: string; text: string; badge: string }> = {
  LOW: {
    icon:  <Info className="w-4 h-4" aria-hidden />,
    border: "border-sky-600",
    bg:     "bg-sky-900/30",
    text:   "text-sky-300",
    badge:  "bg-sky-800 text-sky-200",
  },
  MEDIUM: {
    icon:  <AlertCircle className="w-4 h-4" aria-hidden />,
    border: "border-amber-500",
    bg:     "bg-amber-900/30",
    text:   "text-amber-300",
    badge:  "bg-amber-800 text-amber-200",
  },
  HIGH: {
    icon:  <AlertTriangle className="w-4 h-4" aria-hidden />,
    border: "border-orange-500",
    bg:     "bg-orange-900/30",
    text:   "text-orange-300",
    badge:  "bg-orange-800 text-orange-200",
  },
  CRITICAL: {
    icon:  <AlertTriangle className="w-4 h-4" aria-hidden />,
    border: "border-red-500",
    bg:     "bg-red-900/30",
    text:   "text-red-300",
    badge:  "bg-red-800 text-red-200",
  },
};

const SEV_ORDER: Record<AlertSeverity, number> = {
  CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3,
};

// ---------------------------------------------------------------------------
// Single alert row
// ---------------------------------------------------------------------------

interface AlertRowProps {
  alert: AlertData;
  isAcking: boolean;
  onAck: (id: string) => void;
}

const AlertRow = memo(function AlertRow({ alert, isAcking, onAck }: AlertRowProps) {
  const cfg = SEV[alert.severity];
  return (
    <li
      className={`
        p-3 rounded-lg border-l-4 border border-slate-700
        ${cfg.border} ${cfg.bg}
        transition-all
      `}
      aria-label={`${alert.severity} alert: ${alert.title}`}
    >
      <div className="flex items-start gap-2">
        <span className={`${cfg.text} mt-0.5 shrink-0`}>{cfg.icon}</span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <p className="text-sm font-semibold text-slate-100 truncate">
              {alert.title}
            </p>
            <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${cfg.badge}`}>
              {alert.severity}
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{alert.message}</p>

          {alert.metric && (
            <p className="text-xs text-slate-500 mt-0.5">
              {alert.metric}: {alert.value ?? "—"}
              {alert.threshold != null && ` (limit: ${alert.threshold})`}
            </p>
          )}

          {alert.recommended_action && (
            <p className="text-xs text-slate-500 italic mt-1">
              💡 {alert.recommended_action}
            </p>
          )}

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-600">
              {alert.triggered_at ? formatTime(alert.triggered_at) : ""}
            </span>
            <button
              id={`ack-${alert.alert_id}`}
              onClick={() => onAck(alert.alert_id)}
              disabled={isAcking}
              aria-label={`Acknowledge alert: ${alert.title}`}
              className="
                inline-flex items-center gap-1 px-2 py-0.5
                rounded border border-slate-600 bg-slate-700/60
                text-xs text-slate-300 hover:text-white hover:border-slate-500
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors
              "
            >
              {isAcking ? (
                <>Acknowledging…</>
              ) : (
                <><Check className="w-3 h-3" aria-hidden /> Acknowledge</>
              )}
            </button>
          </div>
        </div>
      </div>
    </li>
  );
});

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface AlertPanelProps {
  alerts: Map<string, AlertData>;
  onAcknowledge: (alertId: string) => void;
}

export const AlertPanel = memo(function AlertPanel({
  alerts,
  onAcknowledge,
}: AlertPanelProps) {
  const [acking, setAcking] = useState<Set<string>>(new Set());

  const handleAck = useCallback((id: string) => {
    setAcking((p) => new Set(p).add(id));
    onAcknowledge(id);
    // Optimistically remove "acking" state after 3 s
    setTimeout(() => {
      setAcking((p) => { const n = new Set(p); n.delete(id); return n; });
    }, 3000);
  }, [onAcknowledge]);

  const sorted = [...alerts.values()].sort(
    (a, b) => SEV_ORDER[a.severity] - SEV_ORDER[b.severity]
  );

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <Bell className="w-4 h-4 text-slate-400" aria-hidden />
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
          Active Alerts
        </h3>
        {sorted.length > 0 && (
          <span className="ml-auto text-xs font-bold bg-red-800 text-red-200 px-1.5 py-0.5 rounded">
            {sorted.length}
          </span>
        )}
      </div>

      {sorted.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center py-8 text-slate-600 gap-1">
          <Bell className="w-8 h-8 opacity-30" aria-hidden />
          <p className="text-sm">No active alerts</p>
          <p className="text-xs">All systems normal</p>
        </div>
      ) : (
        <ul
          role="list"
          aria-label="Active alerts"
          className="space-y-2 overflow-y-auto max-h-80 pr-1"
        >
          {sorted.map((alert) => (
            <AlertRow
              key={alert.alert_id}
              alert={alert}
              isAcking={acking.has(alert.alert_id)}
              onAck={handleAck}
            />
          ))}
        </ul>
      )}
    </div>
  );
});
