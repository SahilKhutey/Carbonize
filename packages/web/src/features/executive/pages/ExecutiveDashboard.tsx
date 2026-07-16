/**
 * packages/web/src/features/executive/pages/ExecutiveDashboard.tsx
 *
 * Route: /executive/dashboard
 *
 * Portfolio-level BI view:
 *   ExecNav (sticky top)
 *   GlobalFilters  (period / region / plant selector)
 *   PortfolioKPIs  (6 hero cards)
 *   PlantTable     (sortable, filterable, exportable)
 *   AutoInsights   (AI-generated)
 *   Action bar     (generate report, export, configure)
 */

import React, { useState } from "react";
import { ExecNav }        from "../components/ExecNav";
import { PortfolioKPIs }  from "../components/PortfolioKPIs";
import { PlantTable }     from "../components/PlantTable";
import { AutoInsights }   from "../components/AutoInsights";
import { usePortfolioData } from "../hooks/usePortfolioData";
import { FileText, Download, Settings, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function ExecSkeleton() {
  return (
    <div className="animate-pulse p-6 flex flex-col gap-6" role="status" aria-label="Loading dashboard">
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => <div key={i} className="h-28 rounded-2xl bg-slate-800/60" />)}
      </div>
      <div className="h-64 rounded-xl bg-slate-800/60" />
      <div className="h-32 rounded-xl bg-slate-800/60" />
      <span className="sr-only">Loading…</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function ExecutiveDashboard() {
  const navigate = useNavigate();
  const { summary, plants, insights, loading, error, refresh } = usePortfolioData();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <ExecNav />

      <main className="max-w-screen-2xl mx-auto px-6 py-6 space-y-8">

        {/* Page header */}
        <div className="flex items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">Portfolio Dashboard</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {summary
                ? `Last updated ${new Date(summary.lastUpdated).toLocaleTimeString()}`
                : "Loading…"}
            </p>
          </div>
          <button
            onClick={refresh}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-400 hover:text-white transition-colors"
            aria-label="Refresh dashboard"
          >
            <RefreshCw className="w-3.5 h-3.5" aria-hidden />
            Refresh
          </button>
        </div>

        {/* Error */}
        {error && (
          <div role="alert" className="bg-red-900/40 border border-red-700 rounded-xl px-4 py-3 text-sm text-red-300">
            Failed to load data: {error}
          </div>
        )}

        {loading && !summary ? (
          <ExecSkeleton />
        ) : (
          <>
            {/* Hero KPIs */}
            {summary && <PortfolioKPIs data={summary} />}

            {/* Plant Table */}
            <PlantTable plants={plants} />

            {/* Insights */}
            {insights.length > 0 && <AutoInsights insights={insights} />}

            {/* Action bar */}
            <div
              role="toolbar"
              aria-label="Dashboard actions"
              className="flex flex-wrap gap-3 pt-2 border-t border-slate-800"
            >
              <button
                id="generate-board-report"
                onClick={() => navigate("/executive/reports")}
                className="
                  flex items-center gap-2 px-4 py-2.5 rounded-xl
                  bg-emerald-700 hover:bg-emerald-600 text-white text-sm font-semibold
                  transition-colors
                "
              >
                <FileText className="w-4 h-4" aria-hidden />
                Generate Board Report
              </button>
              <button
                id="export-portfolio-csv"
                className="
                  flex items-center gap-2 px-4 py-2.5 rounded-xl
                  bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm font-medium
                  border border-slate-600 transition-colors
                "
                onClick={() => {
                  // Re-uses PlantTable export — could also POST to backend for richer export
                  const btn = document.getElementById("export-plants-csv") as HTMLButtonElement;
                  btn?.click();
                }}
              >
                <Download className="w-4 h-4" aria-hidden />
                Export Data
              </button>
              <button
                onClick={() => navigate("/executive/alerts")}
                className="
                  flex items-center gap-2 px-4 py-2.5 rounded-xl
                  bg-slate-800 hover:bg-slate-700 text-slate-400 text-sm font-medium
                  border border-slate-700 transition-colors
                "
              >
                <Settings className="w-4 h-4" aria-hidden />
                Configure Alerts
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
