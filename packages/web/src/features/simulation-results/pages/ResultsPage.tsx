/**
 * packages/web/src/features/simulation-results/pages/ResultsPage.tsx
 *
 * Route: /simulations/:id/results  (or /simulations/:id after completion)
 *
 * Three-tab layout:
 *   1. KPIs         — 8 enhanced KPI cards, all showing UQ
 *   2. Distributions — 4 DistributionCharts + optional CI Band charts
 *   3. Sensitivity   — Sobol tornado for CO₂ capture + NPV
 *
 * Uses mock data by default; swap generateMockResult() for fetchSimulationResult(id).
 */

import React, { useState, useCallback, useMemo } from "react";
import { useParams, NavLink } from "react-router-dom";
import {
  Download, FileText, ChevronLeft, BarChart3,
  FlaskConical, TrendingUp, Layers,
} from "lucide-react";
import { KpiCard }              from "../components/KpiCard";
import { DistributionChart }    from "../components/uncertainty/DistributionChart";
import { ConfidenceBandChart }  from "../components/uncertainty/ConfidenceBand";
import { SobolTornadoChart }    from "../components/uncertainty/SobolTornadoChart";
import { generateMockResult }   from "../utils/mockData";
import { ci90HalfWidth }        from "../types/results";
import type { SimulationResult } from "../types/results";

// ---------------------------------------------------------------------------
// Tab definition
// ---------------------------------------------------------------------------

type TabId = "kpis" | "distributions" | "trends" | "sensitivity";

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: "kpis",          label: "KPIs",          icon: <Layers   className="w-3.5 h-3.5" /> },
  { id: "distributions", label: "Distributions",  icon: <BarChart3 className="w-3.5 h-3.5" /> },
  { id: "trends",        label: "Trends",         icon: <TrendingUp className="w-3.5 h-3.5" /> },
  { id: "sensitivity",   label: "Critical Experiments", icon: <FlaskConical className="w-3.5 h-3.5" /> },
];

// ---------------------------------------------------------------------------
// Distribution modal
// ---------------------------------------------------------------------------

function DistributionModal({
  metric,
  label,
  unit,
  target,
  onClose,
}: {
  metric: ReturnType<typeof generateMockResult>["capture"]["co2_pct"];
  label: string;
  unit: string;
  target?: number;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal
      aria-label={`${label} distribution detail`}
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div className="relative z-10 w-full max-w-2xl mx-4">
        <DistributionChart
          title={`${label} — Full Distribution`}
          samples={metric.samples}
          unit={unit}
          target={target}
          numBins={25}
          height={340}
        />
        <button
          onClick={onClose}
          className="
            absolute top-3 right-4
            text-xs text-slate-400 hover:text-white
            bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5
            transition-colors
          "
        >
          Close ✕
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface ModalState {
  metric: SimulationResult["capture"]["co2_pct"];
  label: string;
  unit: string;
  target?: number;
}

export function ResultsPage() {
  const { id } = useParams<{ id: string }>();

  // In production: const result = useSimulationResult(id);
  const result: SimulationResult = useMemo(
    () => generateMockResult(42, 500),
    [],
  );

  const [activeTab, setActiveTab] = useState<TabId>("kpis");
  const [modal, setModal]         = useState<ModalState | null>(null);

  const openModal = useCallback((m: ModalState) => setModal(m), []);
  const closeModal = useCallback(() => setModal(null), []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">

      {/* ── Header ── */}
      <header className="
        sticky top-0 z-30
        bg-slate-900/95 backdrop-blur-md
        border-b border-slate-800
        px-6 py-3
        flex items-center gap-4
      ">
        <NavLink
          to="/simulations"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" aria-hidden /> Simulations
        </NavLink>

        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-white truncate">
            {result.plant_name}
          </h1>
          <p className="text-[10px] text-slate-500 font-mono">
            {result.n_samples.toLocaleString()} samples ·{" "}
            {result.duration_s}s ·{" "}
            {new Date(result.completed_at).toLocaleString()}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="
            flex items-center gap-1.5 px-3 py-1.5 rounded-lg
            bg-slate-800 border border-slate-700
            text-xs text-slate-300 hover:text-white
            hover:bg-slate-700 transition-colors
          ">
            <Download className="w-3.5 h-3.5" aria-hidden /> CSV
          </button>
          <button className="
            flex items-center gap-1.5 px-3 py-1.5 rounded-lg
            bg-slate-800 border border-slate-700
            text-xs text-slate-300 hover:text-white
            hover:bg-slate-700 transition-colors
          ">
            <FileText className="w-3.5 h-3.5" aria-hidden /> PDF Report
          </button>
        </div>
      </header>

      {/* ── Tabs ── */}
      <div className="sticky top-14 z-20 bg-slate-950 border-b border-slate-800 px-6">
        <div className="flex gap-1 overflow-x-auto py-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              aria-selected={activeTab === tab.id}
              className={`
                flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold
                whitespace-nowrap transition-all
                ${activeTab === tab.id
                  ? "bg-emerald-700/30 text-emerald-300 border border-emerald-700"
                  : "text-slate-500 hover:text-slate-300 hover:bg-slate-800/60"}
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      <main className="max-w-7xl mx-auto px-6 py-6">

        {/* KPIs tab */}
        {activeTab === "kpis" && (
          <div className="space-y-6">
            {/* Capture */}
            <section aria-labelledby="capture-heading">
              <h2 id="capture-heading" className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Pollutant Capture
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiCard
                  label="CO₂ Capture"
                  metric={result.capture.co2_pct}
                  unit="%"
                  target={85}
                  onClick={() => openModal({ metric: result.capture.co2_pct, label: "CO₂ Capture", unit: "%", target: 85 })}
                />
                <KpiCard
                  label="SO₂ Capture"
                  metric={result.capture.so2_pct}
                  unit="%"
                  target={90}
                  onClick={() => openModal({ metric: result.capture.so2_pct, label: "SO₂ Capture", unit: "%", target: 90 })}
                />
                <KpiCard
                  label="NOₓ Removal"
                  metric={result.capture.nox_pct}
                  unit="%"
                  target={70}
                  onClick={() => openModal({ metric: result.capture.nox_pct, label: "NOₓ Removal", unit: "%" })}
                />
                <KpiCard
                  label="Heavy Metal Removal"
                  metric={result.capture.hm_pct}
                  unit="%"
                  target={90}
                  onClick={() => openModal({ metric: result.capture.hm_pct, label: "Heavy Metal Removal", unit: "%", target: 90 })}
                />
              </div>
            </section>

            {/* Block */}
            <section aria-labelledby="block-heading">
              <h2 id="block-heading" className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Block Properties
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <KpiCard
                  label="Block Compressive Strength"
                  metric={result.block.strength_mpa}
                  unit=" MPa"
                  target={20}
                  precision={1}
                  onClick={() => openModal({ metric: result.block.strength_mpa, label: "Block Strength", unit: " MPa", target: 20 })}
                />
                <KpiCard
                  label="Block Output"
                  metric={result.block.output_kg_per_day}
                  unit=" kg/day"
                  precision={0}
                  onClick={() => openModal({ metric: result.block.output_kg_per_day, label: "Block Output", unit: " kg/day" })}
                />
              </div>
            </section>

            {/* Economics */}
            <section aria-labelledby="econ-heading">
              <h2 id="econ-heading" className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Financial
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiCard
                  label="10-Year NPV"
                  metric={{
                    ...result.economic.npv_10yr_inr,
                    mean: result.economic.npv_10yr_inr.mean / 1e7,
                    p5:   result.economic.npv_10yr_inr.p5 / 1e7,
                    p25:  result.economic.npv_10yr_inr.p25 / 1e7,
                    p50:  result.economic.npv_10yr_inr.p50 / 1e7,
                    p75:  result.economic.npv_10yr_inr.p75 / 1e7,
                    p95:  result.economic.npv_10yr_inr.p95 / 1e7,
                    std:  result.economic.npv_10yr_inr.std / 1e7,
                    samples: result.economic.npv_10yr_inr.samples.map(v => v / 1e7),
                  }}
                  unit=" Cr"
                  target={1.0}
                  precision={2}
                  onClick={() => openModal({
                    metric: {
                      ...result.economic.npv_10yr_inr,
                      mean: result.economic.npv_10yr_inr.mean / 1e7,
                      p5:   result.economic.npv_10yr_inr.p5 / 1e7,
                      p95:  result.economic.npv_10yr_inr.p95 / 1e7,
                      p25:  result.economic.npv_10yr_inr.p25 / 1e7,
                      p50:  result.economic.npv_10yr_inr.p50 / 1e7,
                      p75:  result.economic.npv_10yr_inr.p75 / 1e7,
                      std:  result.economic.npv_10yr_inr.std / 1e7,
                      samples: result.economic.npv_10yr_inr.samples.map(v => v / 1e7),
                    },
                    label: "10-Year NPV",
                    unit: " Cr",
                    target: 1.0,
                  })}
                />
                <KpiCard
                  label="IRR"
                  metric={result.economic.irr_pct}
                  unit="%"
                  target={18}
                  precision={1}
                />
                <KpiCard
                  label="CCTS Credits"
                  metric={result.economic.ccts_credits_yr}
                  unit=" tonnes/yr"
                  precision={0}
                />
                <KpiCard
                  label="Payback Period"
                  metric={result.economic.payback_years}
                  unit=" yrs"
                  target={5}
                  lowIsGood
                  precision={1}
                />
              </div>
            </section>
          </div>
        )}

        {/* Distributions tab */}
        {activeTab === "distributions" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <DistributionChart
              title="CO₂ Capture Efficiency"
              samples={result.capture.co2_pct.samples}
              unit="%"
              target={85}
              targetLabel="CPCB limit"
            />
            <DistributionChart
              title="SO₂ Capture Efficiency"
              samples={result.capture.so2_pct.samples}
              unit="%"
              target={90}
            />
            <DistributionChart
              title="Block Compressive Strength"
              samples={result.block.strength_mpa.samples}
              unit=" MPa"
              target={20}
              targetLabel="IS 1077 M20"
            />
            <DistributionChart
              title="10-Year NPV"
              samples={result.economic.npv_10yr_inr.samples.map(v => +(v / 1e7).toFixed(2))}
              unit=" Cr"
              target={1.0}
              targetLabel="Break-even"
            />
          </div>
        )}

        {/* Trends tab */}
        {activeTab === "trends" && (
          <div className="space-y-5">
            <ConfidenceBandChart
              title="CO₂ Capture Over Time"
              data={result.time_series.co2_capture}
              unit="%"
              xLabel="Operating hours"
              target={85}
              targetLabel="CPCB target"
            />
            <ConfidenceBandChart
              title="SO₂ Capture Over Time"
              data={result.time_series.so2_capture}
              unit="%"
              xLabel="Operating hours"
              target={90}
            />
            <ConfidenceBandChart
              title="Block Strength Progression"
              data={result.time_series.block_strength}
              unit=" MPa"
              xLabel="Operating hours"
              target={20}
              targetLabel="IS 1077 M20"
            />
          </div>
        )}

        {/* Sensitivity tab */}
        {activeTab === "sensitivity" && (
          <div className="space-y-5">
            <SobolTornadoChart
              outputName="CO₂ Capture"
              outputUnit="%"
              indices={result.sensitivity.co2_capture_indices}
              onParameterClick={(p) => console.info("Drill into", p)}
            />
            <SobolTornadoChart
              outputName="10-Year NPV"
              outputUnit=" Cr"
              indices={result.sensitivity.npv_indices}
              onParameterClick={(p) => console.info("Drill into", p)}
            />
          </div>
        )}

      </main>

      {/* ── Distribution modal ── */}
      {modal && (
        <DistributionModal
          metric={modal.metric}
          label={modal.label}
          unit={modal.unit}
          target={modal.target}
          onClose={closeModal}
        />
      )}
    </div>
  );
}
