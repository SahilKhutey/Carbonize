/**
 * Statistical and uncertainty utilities for simulation results.
 */

import type { UQMetric, SobolIndex } from "../types/results";

export function mulberry32(a: number) {
  return function () {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function makeNormalSamples(rand: () => number, n: number, mean: number, std: number): number[] {
  const arr: number[] = [];
  for (let i = 0; i < n; i++) {
    const u1 = Math.max(1e-9, rand());
    const u2 = rand();
    const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    arr.push(mean + z * std);
  }
  return arr;
}

export function uqFromSamples(samples: number[]): UQMetric {
  const sorted = [...samples].sort((a, b) => a - b);
  const n = sorted.length;
  const mean = samples.reduce((a, b) => a + b, 0) / n;
  const variance = samples.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / n;
  const std = Math.sqrt(variance);

  const idx = (pct: number) => Math.min(n - 1, Math.max(0, Math.floor((pct / 100) * n)));

  return {
    mean,
    std,
    cv: std / Math.abs(mean || 1),
    p5: sorted[idx(5)],
    p25: sorted[idx(25)],
    p50: sorted[idx(50)],
    p75: sorted[idx(75)],
    p95: sorted[idx(95)],
    samples,
  };
}

export function makeSobolIndices(rand: () => number): SobolIndex[] {
  const params = [
    { parameter: "enzyme_concentration_mg_l", label: "Enzyme Conc. (mg/L)", unit: "mg/L" },
    { parameter: "reactor_temp_c",             label: "Reactor Temp (°C)",   unit: "°C" },
    { parameter: "flow_rate_nm3_hr",           label: "Flue Gas Flow",       unit: "Nm³/h" },
  ];
  return params.map(p => ({
    ...p,
    s1: 0.1,
    st: 0.15,
    s1_conf: 0.02,
    st_conf: 0.03,
  }));
}
