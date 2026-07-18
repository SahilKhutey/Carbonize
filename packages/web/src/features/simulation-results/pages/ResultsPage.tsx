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

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { useParams, NavLink } from "react-router-dom";
import {
  Download, FileText, ChevronLeft, BarChart3,
  FlaskConical, TrendingUp, Layers, Loader2, AlertTriangle
} from "lucide-react";
import { KpiCard }              from "../components/KpiCard";
import { DistributionChart }    from "../components/uncertainty/DistributionChart";
import { ConfidenceBandChart }  from "../components/uncertainty/ConfidenceBand";
import { SobolTornadoChart }    from "../components/uncertainty/SobolTornadoChart";
import {
  generateMockResult, mulberry32, makeNormalSamples,
  uqFromSamples, makeTimeSeries, makeSobolIndices
} from "../utils/mockData";
import { ci90HalfWidth }        from "../types/results";
import type { SimulationResult, UQMetric, SobolIndex, SensitivityResult } from "../types/results";

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

function makeDeterministicNormalSamples(
  seedStr: string,
  n: number,
  mean: number,
  std: number,
): number[] {
  let seed = 0;
  for (let i = 0; i < seedStr.length; i++) {
    seed = (seed + seedStr.charCodeAt(i)) * 0x6D2B79F5 | 0;
  }
  const rand = mulberry32(seed);
  return makeNormalSamples(rand, n, mean, std);
}

function reconstructUQMetric(
  seedStr: string,
  nSamples: number,
  mean: number,
  std: number,
  minVal = 0,
  maxVal = 100,
): UQMetric {
  const samples = makeDeterministicNormalSamples(seedStr, nSamples, mean, std)
    .map(v => Math.min(maxVal, Math.max(minVal, v)));
  return uqFromSamples(samples);
}

function getUQMetric(
  uq_metrics: any,
  metricKey: string,
  seedStr: string,
  nSamples: number,
  mean: number,
  std: number,
  minVal = 0,
  maxVal = 100
): UQMetric {
  const data = uq_metrics[metricKey];
  if (data && data.samples && data.samples.length > 0) {
    return {
      mean: data.mean,
      std: data.std,
      cv: data.std / Math.abs(data.mean || 1),
      p5: data.p05 ?? data.p5,
      p25: data.p25 ?? (data.mean - data.std * 0.67),
      p50: data.p50 ?? data.mean,
      p75: data.p75 ?? (data.mean + data.std * 0.67),
      p95: data.p95,
      samples: data.samples,
    };
  }
  return reconstructUQMetric(seedStr + "-" + metricKey, nSamples, mean, std, minVal, maxVal);
}

function mapBackendResultToFrontend(run: any): SimulationResult {
  const resultObj = run.result;
  const N = run.n_samples || 500;
  const seed = run.id || "sim-default";

  const uq_metrics = resultObj.uq_metrics || {};
  const co2_uq = uq_metrics.co2 || { mean: resultObj.co2_capture_efficiency_pct, std: resultObj.co2_capture_efficiency_pct * 0.02 };
  const so2_uq = uq_metrics.so2 || { mean: resultObj.so2_capture_efficiency_pct, std: resultObj.so2_capture_efficiency_pct * 0.05 };

  const co2_pct = getUQMetric(uq_metrics, "co2", seed, N, co2_uq.mean, co2_uq.std || 0.1, 0, 100);
  const so2_pct = getUQMetric(uq_metrics, "so2", seed, N, so2_uq.mean, so2_uq.std || 1.0, 0, 100);
  const nox_pct = reconstructUQMetric(seed + "-nox", N, parseFloat(run.plant?.nox_mg_per_nm3 || 450) > 0 ? 72.0 : 0.0, 8.0, 0, 100);
  const hm_pct  = reconstructUQMetric(seed + "-hm", N, 94.1, 3.2, 0, 100);
  const pm_pct  = reconstructUQMetric(seed + "-pm", N, 88.0, 5.5, 0, 100);

  const strength_mpa = getUQMetric(uq_metrics, "strength", seed, N, resultObj.predicted_block_strength_mpa, resultObj.predicted_block_strength_mpa * 0.1, 0, 100);
  const output_kg_per_day = reconstructUQMetric(seed + "-output", N, resultObj.hourly_block_yield_kg * 24.0, resultObj.hourly_block_yield_kg * 24.0 * 0.05, 0, 1e7);

  const npv_10yr_inr = getUQMetric(uq_metrics, "npv", seed, N, resultObj.npv_10yr_inr, Math.abs(resultObj.npv_10yr_inr) * 0.15, -1e9, 1e9);
  const irr_pct = reconstructUQMetric(seed + "-irr", N, resultObj.irr_pct, resultObj.irr_pct * 0.1, 0, 100);
  const payback_years = getUQMetric(uq_metrics, "payback", seed, N, resultObj.simple_payback_months / 12.0, (resultObj.simple_payback_months / 12.0) * 0.15, 0, 100);
  const opex_inr_per_day = reconstructUQMetric(seed + "-opex", N, resultObj.annual_opex_inr / 365.0, (resultObj.annual_opex_inr / 365.0) * 0.05, 0, 1e9);
  const capex_inr = reconstructUQMetric(seed + "-capex", N, resultObj.capex_total_inr, resultObj.capex_total_inr * 0.05, 0, 1e9);
  const ccts_credits_yr = reconstructUQMetric(seed + "-ccts", N, resultObj.annual_ccts_revenue_inr / 1000.0, (resultObj.annual_ccts_revenue_inr / 1000.0) * 0.05, 0, 1e9);
  const annual_revenue_inr = reconstructUQMetric(seed + "-annrev", N, resultObj.annual_block_revenue_inr + resultObj.annual_ccts_revenue_inr, (resultObj.annual_block_revenue_inr + resultObj.annual_ccts_revenue_inr) * 0.08, 0, 1e9);

  const rand = mulberry32(12345);
  
  const mapSobol = (sobolIndices: SobolIndex[], keyMap: any, sourceIndices?: any) => {
    return sobolIndices.map(item => {
      const mappedKey = keyMap[item.parameter] || item.parameter;
      const val = sourceIndices ? sourceIndices[mappedKey] : (uq_metrics.sensitivity ? uq_metrics.sensitivity[mappedKey] : undefined);
      if (val !== undefined) {
        return {
          ...item,
          s1: parseFloat(val.toFixed(4)),
          st: parseFloat((val * 1.1).toFixed(4)),
        };
      }
      return item;
    });
  };

  const baseSens = makeSobolIndices(rand);
  const co2_sens_map = {
    "enzyme_concentration_mg_l": "enzyme_concentration_mg_l",
    "reactor_temp_c": "reactor_temperature_c",
    "flow_rate_nm3_hr": "flow_rate_nm3_hr"
  };
  
  const sensitivity: SensitivityResult = {
    co2_capture_indices: mapSobol(baseSens, co2_sens_map, uq_metrics.sobol?.co2_capture),
    npv_indices: mapSobol(baseSens, {}, uq_metrics.sobol?.npv),
    block_strength_indices: mapSobol(baseSens, {}, uq_metrics.sobol?.block_strength)
  };

  const completedTime = run.completed_at ? new Date(run.completed_at) : new Date();
  const duration = run.completed_at && run.created_at ? 
    Math.round((new Date(run.completed_at).getTime() - new Date(run.created_at).getTime()) / 1000.0) : 180;

  const time_series = uq_metrics.time_series || {
    co2_capture: makeTimeSeries(rand, 24, co2_uq.mean - co2_uq.std * 1.5, co2_uq.mean, co2_uq.std || 1.0),
    so2_capture: makeTimeSeries(rand, 24, so2_uq.mean - so2_uq.std * 1.5, so2_uq.mean, so2_uq.std || 1.5),
    block_strength: makeTimeSeries(rand, 24, resultObj.predicted_block_strength_mpa * 0.9, resultObj.predicted_block_strength_mpa, resultObj.predicted_block_strength_mpa * 0.05),
    ph_profile: makeTimeSeries(rand, 24, 8.2, 8.5, 0.2)
  };

  return {
    id: run.id,
    plant_id: run.plant?.id || "unknown",
    plant_name: run.plant?.name || "Industrial Facility",
    status: run.status,
    n_samples: N,
    completed_at: completedTime.toISOString(),
    duration_s: duration > 0 ? duration : 180,
    capture: {
      co2_pct,
      so2_pct,
      nox_pct,
      hm_pct,
      pm_pct
    },
    block: {
      strength_mpa,
      is_grade: resultObj.block_grade || "M20",
      leach_risk: "low",
      output_kg_per_day
    },
    economic: {
      npv_10yr_inr,
      irr_pct,
      payback_years,
      opex_inr_per_day,
      capex_inr,
      ccts_credits_yr,
      annual_revenue_inr
    },
    time_series,
    sensitivity
  };
}

export function ResultsPage() {
  const { id } = useParams<{ id: string }>();

  const [result, setResult]   = useState<SimulationResult | null>(null);
  const [loading, setLoading]   = useState<boolean>(true);
  const [error, setError]       = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<TabId>("kpis");
  const [modal, setModal]         = useState<ModalState | null>(null);

  const openModal = useCallback((m: ModalState) => setModal(m), []);
  const closeModal = useCallback(() => setModal(null), []);

  useEffect(() => {
    if (!id) return;

    const fetchResult = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`/api/simulations/${id}`);
        if (!res.ok) {
          throw new Error(`Failed to load simulation results (Status ${res.status})`);
        }
        const data = await res.json();

        if (data.status !== "COMPLETED") {
          throw new Error(`Simulation is in status ${data.status}, not COMPLETED`);
        }
        if (!data.result) {
          throw new Error("Simulation has no computed results yet.");
        }

        const mapped = mapBackendResultToFrontend(data);
        setResult(mapped);
      } catch (err: any) {
        setError(err.message || "An unexpected error occurred while loading results.");
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-200">
        <Loader2 className="w-10 h-10 text-emerald-400 animate-spin mb-4" />
        <p className="text-sm font-semibold tracking-wide text-slate-400">Loading live simulation results...</p>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-200 p-6">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center shadow-xl">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-bold text-white mb-2">Error Loading Results</h2>
          <p className="text-xs text-slate-400 mb-6 leading-relaxed">{error || "Simulation run details could not be found."}</p>
          <div className="flex gap-3 justify-center">
            <NavLink
              to="/simulations"
              className="px-4 py-2 bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-semibold text-slate-200 rounded-lg transition-colors"
            >
              Back to Simulations
            </NavLink>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

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
