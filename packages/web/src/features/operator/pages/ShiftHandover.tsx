/**
 * packages/web/src/features/operator/pages/ShiftHandover.tsx
 *
 * Route: /operator/handover
 *
 * End-of-shift sign-off form.
 * Auto-populates from today's twin state snapshot (passed as props in prod).
 * Posts to /api/handover (placeholder — returns 201 on success).
 */

import React, { useState, useCallback, FormEvent } from "react";
import { NavLink } from "react-router-dom";
import { ChevronLeft, CheckCircle, Loader2 } from "lucide-react";

// ---------------------------------------------------------------------------
// Auto-generated summary (would come from API / twin state in prod)
// ---------------------------------------------------------------------------

const AUTO_SUMMARY = [
  "CO₂ capture avg: 87.2% (target: ≥ 85%) ✅",
  "SO₂ capture avg: 96.5% ✅",
  "2 alarms raised — 2 acknowledged",
  "Pump A stopped 09:32, restarted 09:48 (reagent slug cleared)",
  "Reactor temp stable at 40.2 °C ± 0.4 °C",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

type Status = "idle" | "submitting" | "success" | "error";

export function ShiftHandover() {
  const [outgoing, setOutgoing] = useState("");
  const [incoming, setIncoming] = useState("");
  const [notes, setNotes]       = useState("");
  const [status, setStatus]     = useState<Status>("idle");

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    if (!outgoing.trim() || !incoming.trim()) return;

    setStatus("submitting");
    try {
      // TODO: replace with real API
      await new Promise((r) => setTimeout(r, 800));
      setStatus("success");
    } catch {
      setStatus("error");
    }
  }, [outgoing, incoming, notes]);

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">

      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center gap-4">
        <NavLink
          to="/operator/live"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" aria-hidden /> Live Ops
        </NavLink>
        <h1 className="text-sm font-bold text-white">Shift Handover</h1>
        <span className="ml-auto text-xs text-slate-500">{today}</span>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">

        {status === "success" ? (
          <div
            className="flex flex-col items-center gap-4 py-16 text-center"
            role="status"
            aria-live="polite"
          >
            <CheckCircle className="w-16 h-16 text-emerald-400" aria-hidden />
            <h2 className="text-xl font-bold text-white">Shift Handed Over</h2>
            <p className="text-slate-400 text-sm">
              Handover note saved. Incoming operator notified.
            </p>
            <NavLink
              to="/operator/live"
              className="mt-4 px-6 py-2.5 rounded-xl bg-emerald-700 text-white text-sm font-semibold hover:bg-emerald-600 transition-colors"
            >
              Back to Live Ops
            </NavLink>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Operator names */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="outgoing-operator" className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-widest">
                  Outgoing Operator
                </label>
                <input
                  id="outgoing-operator"
                  type="text"
                  value={outgoing}
                  onChange={(e) => setOutgoing(e.target.value)}
                  required
                  placeholder="Your name"
                  className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-600 text-sm"
                />
              </div>
              <div>
                <label htmlFor="incoming-operator" className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-widest">
                  Incoming Operator
                </label>
                <input
                  id="incoming-operator"
                  type="text"
                  value={incoming}
                  onChange={(e) => setIncoming(e.target.value)}
                  required
                  placeholder="Incoming operator's name"
                  className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-600 text-sm"
                />
              </div>
            </div>

            {/* Auto-summary */}
            <div>
              <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-widest">
                Auto-Generated Shift Summary
              </p>
              <ul className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 space-y-1.5">
                {AUTO_SUMMARY.map((item, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-slate-600 shrink-0">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Notes */}
            <div>
              <label htmlFor="handover-notes" className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-widest">
                Operator Notes
                <span className="ml-2 text-slate-600 normal-case font-normal">(max 1000 chars)</span>
              </label>
              <textarea
                id="handover-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value.slice(0, 1000))}
                rows={5}
                placeholder="Add any observations, unresolved issues, or instructions for the incoming operator…"
                className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-600 text-sm resize-none"
              />
              <p className="text-xs text-slate-600 text-right mt-1">{notes.length}/1000</p>
            </div>

            {status === "error" && (
              <p role="alert" className="text-sm text-red-400">
                Failed to save handover. Please try again.
              </p>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-end">
              <NavLink
                to="/operator/live"
                className="px-4 py-2.5 rounded-xl border border-slate-700 bg-slate-800 text-sm text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </NavLink>
              <button
                type="submit"
                disabled={status === "submitting"}
                className="
                  flex items-center gap-2 px-6 py-2.5 rounded-xl
                  bg-emerald-700 hover:bg-emerald-600
                  text-white text-sm font-semibold
                  disabled:opacity-50 transition-colors
                "
              >
                {status === "submitting" ? (
                  <><Loader2 className="w-4 h-4 animate-spin" aria-hidden /> Saving…</>
                ) : (
                  <>✓ Sign Off &amp; Submit</>
                )}
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
