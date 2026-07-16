/**
 * packages/web/src/features/simulation-results/utils/mockData.ts
 *
 * Deterministic mock data generator for a SimulationResult.
 * Used for the demo results page and unit tests.
 * Replace `fetchSimulationResult(id)` in production.
 */

import type {
  SimulationResult, UQMetric, CaptureResult, BlockResult,
  EconomicResult, TimeSeriesResult, SensitivityResult,
  ConfidenceBandPoint, SobolIndex,
} from "../types/results";

// ---------------------------------------------------------------------------
// Seeded PRNG (Mulberry32 — deterministic, no external dep)
// ---------------------------------------------------------------------------

function mulberry32(seed: number) {
  return function (): number {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------------------
// Normal distribution sample via Box-Muller
// ---------------------------------------------------------------------------

function makeNormalSamples(
  rand: () => number,
  n: number,
  mean: number,
  std: number,
): number[] {
  const out: number[] = [];
  for (let i = 0; i < n; i += 2) {
    const u1 = Math.max(1e-10, rand());
    const u2 = rand();
    const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    const z1 = Math.sqrt(-2 * Math.log(u1)) * Math.sin(2 * Math.PI * u2);
    out.push(mean + z0 * std);
    if (i + 1 < n) out.push(mean + z1 * std);
  }
  return out.slice(0, n);
}

// ---------------------------------------------------------------------------
// Build a UQMetric from samples
// ---------------------------------------------------------------------------

function uqFromSamples(samples: number[]): UQMetric {
  const s = [...samples].sort((a, b) => a - b);
  const n = s.length;
  const mean = s.reduce((a, b) => a + b, 0) / n;
  const variance = s.reduce((acc, x) => acc + (x - mean) ** 2, 0) / n;
  const std = Math.sqrt(variance);
  const pct = (p: number) => s[Math.max(0, Math.floor(n * p) - 1)];
  return {
    mean, std, cv: std / Math.abs(mean || 1),
    p5: pct(0.05), p25: pct(0.25), p50: pct(0.50),
    p75: pct(0.75), p95: pct(0.95),
    samples,
  };
}

// ---------------------------------------------------------------------------
// Time-series generator
// ---------------------------------------------------------------------------

function makeTimeSeries(
  rand: () => number,
  steps: number,
  meanStart: number,
  meanEnd: number,
  std: number,
): ConfidenceBandPoint[] {
  const out: ConfidenceBandPoint[] = [];
  for (let i = 0; i < steps; i++) {
    const t = i / (steps - 1);
    const mu = meanStart + t * (meanEnd - meanStart);
    const u1 = Math.max(1e-10, rand());
    const u2 = rand();
    const noise = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    const median = mu + noise * std * 0.5;
    out.push({
      x: `h${String(i * 2).padStart(2, "0")}`,
      median: parseFloat(median.toFixed(2)),
      p5:     parseFloat((median - std * 1.6).toFixed(2)),
      p95:    parseFloat((median + std * 1.6).toFixed(2)),
    });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Sobol indices
// ---------------------------------------------------------------------------

const SOBOL_PARAMS: Array<Omit<SobolIndex, "s1" | "st" | "s1_conf" | "st_conf">> = [
  { parameter: "enzyme_concentration_mg_l",  label: "Enzyme concentration",  unit: "mg/L",   current_uncertainty: "±30% log-normal" },
  { parameter: "ca2_concentration_mm",        label: "Ca²⁺ concentration",   unit: "mM",     current_uncertainty: "±20% normal"     },
  { parameter: "ph_setpoint",                 label: "pH setpoint",           unit: "",       current_uncertainty: "±0.3 units"      },
  { parameter: "reactor_temp_c",              label: "Reactor temperature",   unit: "°C",     current_uncertainty: "±5°C"            },
  { parameter: "flow_rate_nm3_hr",            label: "Gas flow rate",         unit: "Nm³/hr", current_uncertainty: "±10% orifice"    },
  { parameter: "co2_inlet_pct",               label: "CO₂ inlet %",          unit: "%",      current_uncertainty: "±15% analyser"   },
  { parameter: "chitosan_loading_g_l",        label: "Chitosan loading",      unit: "g/L",    current_uncertainty: "±25% batch"      },
  { parameter: "liquid_gas_ratio",            label: "L/G ratio",             unit: "",       current_uncertainty: "±12% field"      },
];

function makeSobolIndices(rand: () => number): SobolIndex[] {
  // Generate plausible S1 and ST values (ST ≥ S1 always)
  const rawST = SOBOL_PARAMS.map(() => rand() * 0.4 + 0.01);
  const totalST = rawST.reduce((a, b) => a + b, 0);
  return SOBOL_PARAMS.map((p, i) => {
    const st = rawST[i] / (totalST > 1 ? totalST : 1);
    const s1 = st * (0.5 + rand() * 0.4); // S1 always ≤ ST
    return {
      ...p,
      s1: parseFloat(s1.toFixed(4)),
      s1_conf: parseFloat((s1 * 0.1).toFixed(4)),
      st: parseFloat(st.toFixed(4)),
      st_conf: parseFloat((st * 0.1).toFixed(4)),
    };
  });
}

// ---------------------------------------------------------------------------
// Main factory
// ---------------------------------------------------------------------------

export function generateMockResult(seed = 42, nSamples = 500): SimulationResult {
  const rand = mulberry32(seed);
  const N = nSamples;

  const co2CaptureSamples   = makeNormalSamples(rand, N, 87.2, 4.5).map(v => Math.min(100, Math.max(0, v)));
  const so2CaptureSamples   = makeNormalSamples(rand, N, 96.5, 2.1).map(v => Math.min(100, Math.max(0, v)));
  const noxCaptureSamples   = makeNormalSamples(rand, N, 72.0, 8.0).map(v => Math.min(100, Math.max(0, v)));
  const hmCaptureSamples    = makeNormalSamples(rand, N, 94.1, 3.2).map(v => Math.min(100, Math.max(0, v)));
  const pmCaptureSamples    = makeNormalSamples(rand, N, 88.0, 5.5).map(v => Math.min(100, Math.max(0, v)));
  const strengthSamples     = makeNormalSamples(rand, N, 22.4, 3.1).map(v => Math.max(0, v));
  const blockOutputSamples  = makeNormalSamples(rand, N, 480,  45 ).map(v => Math.max(0, v));
  const npvSamples          = makeNormalSamples(rand, N, 1.85e7, 4.2e6);
  const irrSamples          = makeNormalSamples(rand, N, 24.5, 4.1 ).map(v => Math.max(0, v));
  const paybackSamples      = makeNormalSamples(rand, N, 4.2, 0.9  ).map(v => Math.max(0, v));
  const opexSamples         = makeNormalSamples(rand, N, 18000, 2200).map(v => Math.max(0, v));
  const capexSamples        = makeNormalSamples(rand, N, 2.5e6, 3.2e5);
  const cctsYrSamples       = makeNormalSamples(rand, N, 450, 55  ).map(v => Math.max(0, v));
  const revenueYrSamples    = makeNormalSamples(rand, N, 9.2e6, 1.1e6);

  const capture: CaptureResult = {
    co2_pct: uqFromSamples(co2CaptureSamples),
    so2_pct: uqFromSamples(so2CaptureSamples),
    nox_pct: uqFromSamples(noxCaptureSamples),
    hm_pct:  uqFromSamples(hmCaptureSamples),
    pm_pct:  uqFromSamples(pmCaptureSamples),
  };

  const block: BlockResult = {
    strength_mpa:      uqFromSamples(strengthSamples),
    is_grade:          "M20",
    leach_risk:        "low",
    output_kg_per_day: uqFromSamples(blockOutputSamples),
  };

  const economic: EconomicResult = {
    npv_10yr_inr:       uqFromSamples(npvSamples),
    irr_pct:            uqFromSamples(irrSamples),
    payback_years:      uqFromSamples(paybackSamples),
    opex_inr_per_day:   uqFromSamples(opexSamples),
    capex_inr:          uqFromSamples(capexSamples),
    ccts_credits_yr:    uqFromSamples(cctsYrSamples),
    annual_revenue_inr: uqFromSamples(revenueYrSamples),
  };

  const time_series: TimeSeriesResult = {
    co2_capture:    makeTimeSeries(rand, 24, 82, 87.2, 3.5),
    so2_capture:    makeTimeSeries(rand, 24, 94, 96.5, 1.5),
    block_strength: makeTimeSeries(rand, 24, 20, 22.4, 2.2),
    ph_profile:     makeTimeSeries(rand, 24, 8.2, 8.5, 0.2),
  };

  const sensitivity: SensitivityResult = {
    co2_capture_indices:    makeSobolIndices(rand),
    npv_indices:            makeSobolIndices(rand),
    block_strength_indices: makeSobolIndices(rand),
  };

  return {
    id:           "sim-mock-001",
    plant_id:     "plant-alpha",
    plant_name:   "Alpha Plant — Pune, MH",
    status:       "COMPLETE",
    n_samples:    N,
    completed_at: new Date().toISOString(),
    duration_s:   187,
    capture,
    block,
    economic,
    time_series,
    sensitivity,
  };
}
