/**
 * packages/web/src/features/executive/components/PlantTable.tsx
 *
 * Sortable, filterable plant portfolio table with export-to-CSV.
 * Executive view — all plants at a glance.
 */

import React, { memo, useState, useMemo, useCallback } from "react";
import { ChevronUp, ChevronDown, Download, Search } from "lucide-react";
import type { PlantRow, PlantStatus } from "../types/executive";
import { useNavigate } from "react-router-dom";

// ---------------------------------------------------------------------------
// Status config (BI color semantics — informational, not alarm)
// ---------------------------------------------------------------------------

const STATUS_CFG: Record<PlantStatus, { label: string; dot: string; text: string }> = {
  ok:      { label: "OK",      dot: "bg-emerald-500", text: "text-emerald-400" },
  warning: { label: "Warning", dot: "bg-amber-400",   text: "text-amber-400"   },
  fault:   { label: "Fault",   dot: "bg-red-500",     text: "text-red-400"     },
  offline: { label: "Offline", dot: "bg-slate-600",   text: "text-slate-500"   },
};

// ---------------------------------------------------------------------------
// Sort
// ---------------------------------------------------------------------------

type SortKey = keyof PlantRow;
type SortDir = "asc" | "desc";

// ---------------------------------------------------------------------------
// CSV export
// ---------------------------------------------------------------------------

function exportCSV(plants: PlantRow[]) {
  const header = "Plant,Location,Status,CO2 Capture %,NPV (Cr/yr),CCTS (t),Last Maint (days)";
  const rows = plants.map((p) =>
    [p.name, p.location, p.status, p.co2CapturePct, p.npvCrorePerYear, p.cctsTonnes, p.lastMaintenanceDaysAgo].join(",")
  );
  const csv = [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "plants.csv"; a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface PlantTableProps {
  plants: PlantRow[];
}

type SortState = { key: SortKey; dir: SortDir };

export const PlantTable = memo(function PlantTable({ plants }: PlantTableProps) {
  const navigate = useNavigate();
  const [sort, setSort] = useState<SortState>({ key: "name", dir: "asc" });
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<PlantStatus | "all">("all");

  const toggleSort = useCallback((key: SortKey) => {
    setSort((prev) =>
      prev.key === key
        ? { key, dir: prev.dir === "asc" ? "desc" : "asc" }
        : { key, dir: "asc" }
    );
  }, []);

  const filtered = useMemo(() => {
    let result = plants;
    if (statusFilter !== "all") result = result.filter((p) => p.status === statusFilter);
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter((p) => p.name.toLowerCase().includes(q) || p.location.toLowerCase().includes(q));
    }
    return [...result].sort((a, b) => {
      const av = a[sort.key], bv = b[sort.key];
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sort.dir === "asc" ? cmp : -cmp;
    });
  }, [plants, sort, search, statusFilter]);

  function SortIcon({ col }: { col: SortKey }) {
    if (sort.key !== col) return <span className="w-3 h-3" />;
    return sort.dir === "asc"
      ? <ChevronUp className="w-3 h-3 text-emerald-400" aria-hidden />
      : <ChevronDown className="w-3 h-3 text-emerald-400" aria-hidden />;
  }

  function Th({ col, label }: { col: SortKey; label: string }) {
    return (
      <th
        scope="col"
        aria-sort={sort.key === col ? (sort.dir === "asc" ? "ascending" : "descending") : "none"}
        className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-white transition-colors"
        onClick={() => toggleSort(col)}
      >
        <span className="inline-flex items-center gap-1">
          {label} <SortIcon col={col} />
        </span>
      </th>
    );
  }

  return (
    <section aria-label="Plant portfolio table">
      {/* Controls */}
      <div className="flex flex-wrap gap-3 mb-3 items-center">
        {/* Search */}
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" aria-hidden />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search plants…"
            className="
              w-full pl-8 pr-3 py-2 text-sm rounded-lg
              bg-slate-800 border border-slate-700 text-slate-200
              placeholder:text-slate-600
              focus:outline-none focus:ring-2 focus:ring-emerald-600
            "
            aria-label="Search plants"
          />
        </div>

        {/* Status filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as PlantStatus | "all")}
          className="
            px-3 py-2 text-sm rounded-lg
            bg-slate-800 border border-slate-700 text-slate-300
            focus:outline-none focus:ring-2 focus:ring-emerald-600
          "
          aria-label="Filter by status"
        >
          <option value="all">All statuses</option>
          <option value="ok">OK</option>
          <option value="warning">Warning</option>
          <option value="fault">Fault</option>
          <option value="offline">Offline</option>
        </select>

        {/* Export */}
        <button
          id="export-plants-csv"
          onClick={() => exportCSV(filtered)}
          className="
            flex items-center gap-2 px-3 py-2 rounded-lg
            bg-slate-700 border border-slate-600 text-slate-300 text-sm font-medium
            hover:bg-slate-600 transition-colors
          "
          aria-label="Export visible plants as CSV"
        >
          <Download className="w-3.5 h-3.5" aria-hidden /> Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-sm" aria-label="Plant portfolio">
          <thead className="bg-slate-800/80 border-b border-slate-700">
            <tr>
              <Th col="name" label="Plant" />
              <Th col="status" label="Status" />
              <Th col="co2CapturePct" label="CO₂ Capture" />
              <Th col="npvCrorePerYear" label="NPV / yr" />
              <Th col="cctsTonnes" label="CCTS" />
              <Th col="lastMaintenanceDaysAgo" label="Last Maint" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-600 text-sm">
                  No plants match your filter.
                </td>
              </tr>
            ) : (
              filtered.map((plant) => {
                const cfg = STATUS_CFG[plant.status];
                return (
                  <tr
                    key={plant.id}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                    onClick={() => navigate(`/executive/plants/${plant.id}`)}
                    aria-label={`View details for ${plant.name}`}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-200">{plant.name}</p>
                      <p className="text-xs text-slate-500">{plant.location}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`flex items-center gap-1.5 ${cfg.text}`}>
                        <span className={`w-2 h-2 rounded-full ${cfg.dot}`} aria-hidden />
                        {cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 tabular-nums font-semibold text-slate-200">
                      {plant.co2CapturePct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 tabular-nums text-slate-300">
                      ₹{plant.npvCrorePerYear.toFixed(1)} Cr
                    </td>
                    <td className="px-4 py-3 tabular-nums text-slate-300">
                      {plant.cctsTonnes} t
                    </td>
                    <td className="px-4 py-3 tabular-nums text-slate-400">
                      {plant.lastMaintenanceDaysAgo} days
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <p className="mt-2 text-xs text-slate-600 text-right">
        {filtered.length} of {plants.length} plants shown
      </p>
    </section>
  );
});
