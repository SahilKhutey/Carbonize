/**
 * packages/web/src/features/operator/pages/AlarmHistory.tsx
 *
 * Route: /operator/alarms
 *
 * Paginated alarm audit log with severity filters and CSV export.
 * Real API integration with backend pagination and filtering.
 */

import React, { useState, useMemo, useCallback, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { Download, ChevronLeft, ChevronRight, Loader2, AlertTriangle } from "lucide-react";
import type { AlarmHistoryEntry } from "../types/operator";



// ---------------------------------------------------------------------------
// CSV export
// ---------------------------------------------------------------------------

function exportCSV(alarms: AlarmHistoryEntry[]) {
  const header = "ID,Severity,Title,Message,Triggered At,Resolved At,Resolved By,Resolution";
  const rows = alarms.map((a) =>
    [a.id, a.severity, `"${a.title}"`, `"${a.message}"`,
     a.triggered_at, a.resolved_at ?? "", a.resolved_by ?? "",
     a.resolution_method].join(",")
  );
  const csv = [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "alarm-history.csv"; a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Severity badge
// ---------------------------------------------------------------------------

const SEV_BADGE: Record<string, string> = {
  CRITICAL: "bg-red-800 text-red-200",
  HIGH:     "bg-orange-800 text-orange-200",
  MEDIUM:   "bg-amber-800 text-amber-200",
  LOW:      "bg-sky-800 text-sky-200",
};

const PAGE_SIZE = 10;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AlarmHistory() {
  const [alarms, setAlarms]   = useState<AlarmHistoryEntry[]>([]);
  const [total, setTotal]     = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError]     = useState<string | null>(null);

  const [severity, setSeverity] = useState<string>("all");
  const [page, setPage]         = useState(0);

  const fetchAlarms = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`/api/operator/alarms?severity=${severity}&page=${page}&page_size=${PAGE_SIZE}`);
      if (!res.ok) {
        throw new Error(`Failed to load alarms (Status ${res.status})`);
      }
      const data = await res.json();
      setAlarms(data.alarms || []);
      setTotal(data.total || 0);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred while loading alarms.");
    } finally {
      setLoading(false);
    }
  }, [severity, page]);

  useEffect(() => {
    fetchAlarms();
  }, [fetchAlarms]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleFilterChange = useCallback((v: string) => {
    setSeverity(v);
    setPage(0);
  }, []);

  const handleExportCSV = useCallback(async () => {
    try {
      const res = await fetch(`/api/operator/alarms?severity=${severity}&page=0&page_size=1000`);
      if (!res.ok) throw new Error("Failed to fetch alarm list for export");
      const data = await res.json();
      exportCSV(data.alarms);
    } catch (err: any) {
      alert(err.message || "Failed to export CSV");
    }
  }, [severity]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">

      {/* Simple header */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center gap-4">
        <NavLink
          to="/operator/live"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" aria-hidden /> Live Ops
        </NavLink>
        <h1 className="text-sm font-bold text-white">Alarm History</h1>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-6 space-y-4">

        {/* Controls */}
        <div className="flex flex-wrap gap-3 items-center">
          <select
            value={severity}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="px-3 py-2 text-sm rounded-lg bg-slate-800 border border-slate-700 text-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
            aria-label="Filter by severity"
          >
            <option value="all">All severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-slate-300 text-sm hover:bg-slate-600 transition-colors"
            aria-label="Export alarm history as CSV"
          >
            <Download className="w-3.5 h-3.5" aria-hidden /> Export CSV
          </button>

          <span className="ml-auto text-xs text-slate-500">
            {total} alarms
          </span>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-xl border border-slate-700">
          <table className="w-full text-sm" aria-label="Alarm history">
            <thead className="bg-slate-800/80 border-b border-slate-700">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest">Time</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest">Severity</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest">Alarm</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest">Resolved</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest">By</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    <Loader2 className="w-5 h-5 text-emerald-400 animate-spin inline mr-2" />
                    Loading alarm records...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-red-400">
                    <AlertTriangle className="w-5 h-5 inline mr-2 text-red-500" />
                    {error}
                  </td>
                </tr>
              ) : alarms.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-600">No alarms match the filter.</td>
                </tr>
              ) : (
                alarms.map((alarm) => (
                  <tr key={alarm.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 tabular-nums text-slate-400 text-xs whitespace-nowrap">
                      {new Date(alarm.triggered_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${SEV_BADGE[alarm.severity] ?? ""}`}>
                        {alarm.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-slate-200 font-medium">{alarm.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{alarm.message}</p>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                      {alarm.resolved_at ? new Date(alarm.resolved_at).toLocaleTimeString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {alarm.resolved_by ?? "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              aria-label="Previous page"
              className="p-2 rounded-lg border border-slate-700 disabled:opacity-30 hover:bg-slate-800 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" aria-hidden />
            </button>
            <span className="text-xs text-slate-400">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              aria-label="Next page"
              className="p-2 rounded-lg border border-slate-700 disabled:opacity-30 hover:bg-slate-800 transition-colors"
            >
              <ChevronRight className="w-4 h-4" aria-hidden />
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
