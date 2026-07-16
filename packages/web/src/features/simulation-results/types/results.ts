/**
 * packages/web/src/features/simulation-results/types/results.ts
 *
 * Domain types for a completed simulation result, including full
 * UQ (uncertainty quantification) distributions for every metric.
 */

// ---------------------------------------------------------------------------
// Primitive UQ metric — returned for every simulation output
// ---------------------------------------------------------------------------

export interface UQMetric {
  /** Point estimate (mean of MC samples) */
  mean: number;
  /** Standard deviation of MC samples */
  std: number;
  /** Coefficient of variation = std / |mean| */
  cv: number;
  /** 5th percentile */
  p5: number;
  /** 25th percentile */
  p25: number;
  /** 50th percentile (median) */
  p50: number;
  /** 75th percentile */
  p75: number;
  /** 95th percentile */
  p95: number;
  /** Full MC sample vector (may be omitted in summary views) */
  samples: number[];
}

// ---------------------------------------------------------------------------
// Time-series point with confidence band
// ---------------------------------------------------------------------------

export interface ConfidenceBandPoint {
  /** x-axis label (e.g. time string or step index) */
  x: string | number;
  /** Median prediction */
  median: number;
  /** P5 lower bound (90% CI lower) */
  p5: number;
  /** P95 upper bound (90% CI upper) */
  p95: number;
  /** Optional observed/actual value for validation overlay */
  actual?: number;
}

// ---------------------------------------------------------------------------
// Sobol sensitivity index for a single parameter
// ---------------------------------------------------------------------------

export interface SobolIndex {
  /** Parameter name (e.g., "enzyme_concentration_mg_l") */
  parameter: string;
  /** Human-readable label */
  label: string;
  /** First-order Sobol index S₁ — direct effect only */
  s1: number;
  /** Confidence interval on S₁ */
  s1_conf: number;
  /** Total-order Sobol index S_T — direct + interactions */
  st: number;
  /** Confidence interval on S_T */
  st_conf: number;
  /** Current assumed uncertainty (for context) */
  current_uncertainty?: string;
  /** Physical units of this parameter */
  unit?: string;
}

// ---------------------------------------------------------------------------
// Full simulation result
// ---------------------------------------------------------------------------

export interface CaptureResult {
  co2_pct: UQMetric;
  so2_pct: UQMetric;
  nox_pct: UQMetric;
  hm_pct:  UQMetric;        // Heavy metal removal
  pm_pct:  UQMetric;        // PM retention
}

export interface BlockResult {
  strength_mpa:      UQMetric;
  is_grade:          string;   // e.g. "M20", "M25"
  leach_risk:        "low" | "medium" | "high";
  output_kg_per_day: UQMetric;
}

export interface EconomicResult {
  npv_10yr_inr:      UQMetric;
  irr_pct:           UQMetric;
  payback_years:     UQMetric;
  opex_inr_per_day:  UQMetric;
  capex_inr:         UQMetric;
  ccts_credits_yr:   UQMetric;
  annual_revenue_inr: UQMetric;
}

export interface TimeSeriesResult {
  co2_capture:    ConfidenceBandPoint[];
  so2_capture:    ConfidenceBandPoint[];
  block_strength: ConfidenceBandPoint[];
  ph_profile:     ConfidenceBandPoint[];
}

export interface SensitivityResult {
  /** Sobol indices for CO₂ capture efficiency */
  co2_capture_indices: SobolIndex[];
  /** Sobol indices for NPV */
  npv_indices:         SobolIndex[];
  /** Sobol indices for block strength */
  block_strength_indices: SobolIndex[];
}

export interface SimulationResult {
  id:            string;
  plant_id:      string;
  plant_name:    string;
  status:        "COMPLETE" | "FAILED" | "RUNNING" | "PENDING";
  n_samples:     number;
  completed_at:  string;
  duration_s:    number;
  capture:       CaptureResult;
  block:         BlockResult;
  economic:      EconomicResult;
  time_series:   TimeSeriesResult;
  sensitivity:   SensitivityResult;
}

// ---------------------------------------------------------------------------
// Confidence level classification
// ---------------------------------------------------------------------------

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

export function classifyConfidence(cv: number): ConfidenceLevel {
  if (cv < 0.10) return "HIGH";
  if (cv < 0.25) return "MEDIUM";
  return "LOW";
}

export function ci90HalfWidth(metric: UQMetric): number {
  return (metric.p95 - metric.p5) / 2;
}
