/**
 * packages/web/src/features/operator/components/ConfirmDialog.tsx
 *
 * Safety confirmation dialog before any actuator action.
 * Prevents accidental actuation in a high-stakes environment.
 *
 * Design: Modal overlay with keyboard trap; Escape cancels.
 */

import React, { memo, useEffect, useRef } from "react";
import { AlertTriangle } from "lucide-react";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog = memo(function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const confirmBtnRef = useRef<HTMLButtonElement>(null);

  // Trap focus inside dialog when open
  useEffect(() => {
    if (isOpen) {
      confirmBtnRef.current?.focus();
    }
  }, [isOpen]);

  // Escape key cancels
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-desc"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={onCancel}
        aria-hidden
      />

      {/* Panel */}
      <div className="
        relative z-10 w-full max-w-sm
        bg-slate-800 border border-slate-700
        rounded-2xl p-6 shadow-2xl
        flex flex-col gap-4
      ">
        {/* Icon + title */}
        <div className="flex items-start gap-3">
          {danger && (
            <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" aria-hidden />
          )}
          <h2
            id="confirm-dialog-title"
            className="text-base font-bold text-white leading-tight"
          >
            {title}
          </h2>
        </div>

        <p id="confirm-dialog-desc" className="text-sm text-slate-300 leading-relaxed">
          {message}
        </p>

        {/* Actions */}
        <div className="flex gap-3 justify-end mt-2">
          <button
            onClick={onCancel}
            className="
              px-4 py-2.5 min-h-[44px] rounded-lg
              border border-slate-600 bg-slate-700
              text-sm font-medium text-slate-300
              hover:bg-slate-600 transition-colors
              focus:outline-none focus:ring-2 focus:ring-slate-500
            "
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmBtnRef}
            onClick={onConfirm}
            className={`
              px-4 py-2.5 min-h-[44px] rounded-lg
              text-sm font-bold transition-colors
              focus:outline-none focus:ring-2
              ${danger
                ? "bg-amber-600 hover:bg-amber-500 text-white focus:ring-amber-500"
                : "bg-emerald-600 hover:bg-emerald-500 text-white focus:ring-emerald-500"
              }
            `}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
});
