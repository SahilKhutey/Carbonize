/**
 * packages/web/src/features/operator/components/AlarmList.tsx
 *
 * Operator DCS alarm side-panel.
 * Shows CRITICAL → HIGH → MEDIUM → LOW, with Acknowledge and Escalate actions.
 * Every action requires confirmation (via ConfirmDialog) and is audited.
 */

import React, { memo, useState, useCallback } from "react";
import { AlertTriangle, AlertCircle, Info, Check, ArrowUpCircle } from "lucide-react";
import type { AlertData, AlertSeverity } from "../../../types/ws";
import { ConfirmDialog } from "./ConfirmDialog";

// ---------------------------------------------------------------------------
// Severity config (DCS alarm semantics — high contrast)
// ---------------------------------------------------------------------------

const SEV_STYLE: Record<AlertSeverity, {
  icon: React.ReactNode;
  border: string;
  bg: string;
  badge: string;
  text: string;
}> = {
  CRITICAL: {
    icon: <AlertTriangle className="w-5 h-5" aria-hidden />,
    border: "border-l-red-500",
    bg: "bg-red-900/40",
    badge: "bg-red-700 text-red-100",
    text: "text-red-300",
  },
  HIGH: {
    icon: <AlertTriangle className="w-5 h-5" aria-hidden />,
    border: "border-l-orange-500",
    bg: "bg-orange-900/40",
    badge: "bg-orange-700 text-orange-100",
    text: "text-orange-300",
  },
  MEDIUM: {
    icon: <AlertCircle className="w-5 h-5" aria-hidden />,
    border: "border-l-amber-500",
    bg: "bg-amber-900/30",
    badge: "bg-amber-700 text-amber-100",
    text: "text-amber-300",
  },
  LOW: {
    icon: <Info className="w-5 h-5" aria-hidden />,
    border: "border-l-sky-500",
    bg: "bg-sky-900/20",
    badge: "bg-sky-800 text-sky-200",
    text: "text-sky-300",
  },
};

const SEV_ORDER: Record<AlertSeverity, number> = {
  CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3,
};

// ---------------------------------------------------------------------------
// Single alarm row
// ---------------------------------------------------------------------------

interface AlarmRowProps {
  alert: AlertData;
  onAck: (id: string) => void;
  onEscalate: (id: string) => void;
  canAcknowledge: boolean;
  canEscalate: boolean;
}

const AlarmRow = memo(function AlarmRow({
  alert, onAck, onEscalate, canAcknowledge, canEscalate,
}: AlarmRowProps) {
  const [pending, setPending] = useState<"ack" | "escalate" | null>(null);
  const [confirm, setConfirm] = useState<"ack" | "escalate" | null>(null);
  const cfg = SEV_STYLE[alert.severity];

  const handleAck = useCallback(() => {
    setPending("ack");
    onAck(alert.alert_id);
    setTimeout(() => setPending(null), 3000);
  }, [onAck, alert.alert_id]);

  const handleEscalate = useCallback(() => {
    setPending("escalate");
    onEscalate(alert.alert_id);
    setTimeout(() => setPending(null), 3000);
  }, [onEscalate, alert.alert_id]);

  return (
    <li
      className={`
        p-3 rounded-xl border border-slate-700 border-l-4
        ${cfg.border} ${cfg.bg}
        transition-all
      `}
      aria-label={`${alert.severity} alarm: ${alert.title}`}
    >
      <div className="flex items-start gap-2">
        <span className={`${cfg.text} shrink-0 mt-0.5`}>{cfg.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${cfg.badge}`}>
              {alert.severity}
            </span>
            <p className="text-sm font-semibold text-slate-100 truncate">
              {alert.title}
            </p>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">{alert.message}</p>

          {alert.metric && (
            <p className="text-xs text-slate-500 mt-0.5">
              {alert.metric}: {alert.value}
              {alert.threshold != null ? ` (limit: ${alert.threshold})` : ""}
            </p>
          )}

          {alert.recommended_action && (
            <p className="text-xs text-slate-400 italic mt-1">
              💡 {alert.recommended_action}
            </p>
          )}

          {/* Actions */}
          <div className="flex gap-2 mt-2">
            {canAcknowledge && (
              <button
                id={`ack-${alert.alert_id}`}
                onClick={() => setConfirm("ack")}
                disabled={!!pending}
                aria-label={`Acknowledge: ${alert.title}`}
                className="
                  flex items-center gap-1.5 px-3 py-2 min-h-[44px] rounded-lg
                  bg-slate-700 border border-slate-600 text-slate-300
                  hover:bg-slate-600 hover:text-white
                  text-xs font-medium transition-colors
                  disabled:opacity-50
                "
              >
                <Check className="w-3.5 h-3.5" aria-hidden />
                {pending === "ack" ? "Acknowledging…" : "Acknowledge"}
              </button>
            )}
            {canEscalate && (
              <button
                id={`escalate-${alert.alert_id}`}
                onClick={() => setConfirm("escalate")}
                disabled={!!pending}
                aria-label={`Escalate: ${alert.title}`}
                className="
                  flex items-center gap-1.5 px-3 py-2 min-h-[44px] rounded-lg
                  bg-orange-900/60 border border-orange-700 text-orange-300
                  hover:bg-orange-800 hover:text-white
                  text-xs font-medium transition-colors
                  disabled:opacity-50
                "
              >
                <ArrowUpCircle className="w-3.5 h-3.5" aria-hidden />
                {pending === "escalate" ? "Escalating…" : "Escalate"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Confirm dialogs */}
      <ConfirmDialog
        isOpen={confirm === "ack"}
        title="Acknowledge Alarm"
        message={`Acknowledge "${alert.title}"? This will be recorded in the audit log.`}
        confirmLabel="Acknowledge"
        onConfirm={() => { setConfirm(null); handleAck(); }}
        onCancel={() => setConfirm(null)}
      />
      <ConfirmDialog
        isOpen={confirm === "escalate"}
        title="Escalate to On-Call Engineer"
        message={`Escalate "${alert.title}" to the on-call engineer? They will be paged immediately.`}
        confirmLabel="Escalate Now"
        danger
        onConfirm={() => { setConfirm(null); handleEscalate(); }}
        onCancel={() => setConfirm(null)}
      />
    </li>
  );
});

// ---------------------------------------------------------------------------
// List
// ---------------------------------------------------------------------------

interface AlarmListProps {
  alerts: Map<string, AlertData>;
  onAcknowledge: (alertId: string) => void;
  onEscalate: (alertId: string) => void;
  canAcknowledge?: boolean;
  canEscalate?: boolean;
}

export const AlarmList = memo(function AlarmList({
  alerts,
  onAcknowledge,
  onEscalate,
  canAcknowledge = false,
  canEscalate = false,
}: AlarmListProps) {
  const sorted = [...alerts.values()].sort(
    (a, b) => SEV_ORDER[a.severity] - SEV_ORDER[b.severity]
  );

  return (
    <div className="bg-slate-900/50 border border-slate-700 rounded-xl h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest flex-1">
          Active Alarms
        </h2>
        {sorted.length > 0 && (
          <span className="text-xs font-bold bg-red-700 text-red-100 px-2 py-0.5 rounded-full">
            {sorted.length}
          </span>
        )}
      </div>

      {sorted.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center py-8 text-slate-600 gap-2">
          <Check className="w-10 h-10 opacity-30" aria-hidden />
          <p className="text-sm font-medium">No active alarms</p>
          <p className="text-xs">All parameters within limits</p>
        </div>
      ) : (
        <ul
          role="list"
          aria-label="Active alarms"
          className="flex-1 overflow-y-auto p-3 space-y-2"
        >
          {sorted.map((alert) => (
            <AlarmRow
              key={alert.alert_id}
              alert={alert}
              onAck={onAcknowledge}
              onEscalate={onEscalate}
              canAcknowledge={canAcknowledge}
              canEscalate={canEscalate}
            />
          ))}
        </ul>
      )}
    </div>
  );
});
