/**
 * packages/web/src/features/simulation-results/components/uncertainty/DistributionChart.tsx
 *
 * Histogram of Monte Carlo samples with:
 *  - 90% CI highlighted bars (green) vs out-of-CI bars (muted)
 *  - P5 / P50 / P95 reference lines
 *  - Mean reference line (dashed)
 *  - Optional target reference line
 *  - ConfidenceIndicator in the header
 *  - 5-stat summary row below (P5 / Median / Mean / P95 / Std)
 *
 * Pure Recharts, no UI library needed.
 */

import React, { useMemo, memo } from "react";
import {
  BarChart, Bar, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { classifyConfidence } from "../../types/results";

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

interface Stats {
  mean: number; std: number; cv: number;
  p5: number; p25: number; p50: number; p75: number; p95: number;
  min: number; max: number;
}

function computeStats(samples: number[]): Stats {
  const s = [...samples].sort((a, b) => a - b);
  const n = s.length;
  const mean = s.reduce((a, b) => a + b, 0) / n;
  const variance = s.reduce((acc, x) => acc + (x - mean) ** 2, 0) / n;
  const std = Math.sqrt(variance);
  const percentile = (p: number) => s[Math.max(0, Math.floor(n * p) - 1)];
  return {
    mean, std,
    cv: std / Math.abs(mean || 1),
    p5: percentile(0.05),
    p25: percentile(0.25),
    p50: percentile(0.50),
    p75: percentile(0.75),
    p95: percentile(0.95),
    min: s[0],
    max: s[n - 1],
  };
}

// ---------------------------------------------------------------------------
// Bins
// ---------------------------------------------------------------------------

interface BinDatum {
  rangeLabel: string;
  lo: number; hi: number; mid: number;
  count: number;
  inCI: boolean;
}

function buildBins(samples: number[], stats: Stats, numBins: number): BinDatum[] {
  const range = Math.max(stats.max - stats.min, 1e-9);
  const w = range / numBins;
  const bins: BinDatum[] = [];
  for (let i = 0; i < numBins; i++) {
    const lo = stats.min + i * w;
    const hi = lo + w;
    const mid = (lo + hi) / 2;
    const count = samples.filter((s) => s >= lo && (i === numBins - 1 ? s <= hi : s < hi)).length;
    bins.push({
      rangeLabel: lo.toFixed(1),
      lo, hi, mid, count,
      inCI: mid >= stats.p5 && mid <= stats.p95,
    });
  }
  return bins;
}

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

function DistTooltip({ active, payload, unit }: { active?: boolean; payload?: any[]; unit: string }) {
  if (!active || !payload?.length) return null;
  const d: BinDatum = payload[0].payload;
  return (
    <div className="
      bg-slate-800 border border-slate-600 rounded-lg p-3
      text-xs text-slate-200 shadow-2xl
    ">
      <p className="font-semibold mb-1">
        {d.lo.toFixed(2)}–{d.hi.toFixed(2)} {unit}
      </p>
      <p>Samples: <span className="font-mono text-white">{d.count}</span></p>
      {d.inCI && (
        <p className="text-emerald-400 mt-0.5">✓ Within 90% CI</p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Stat pill
// ---------------------------------------------------------------------------

function StatPill({
  label, value, unit, highlight,
}: { label: string; value: number; unit: string; highlight?: boolean }) {
  return (
    <div className={`
      flex flex-col items-center px-3 py-2 rounded-lg text-center
      ${highlight
        ? "bg-emerald-900/40 border border-emerald-700"
        : "bg-slate-800/60 border border-slate-700"}
    `}>
      <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">
        {label}
      </span>
      <span className="text-sm font-bold text-white tabular-nums mt-0.5">
        {value.toFixed(2)}<span className="text-xs text-slate-400 ml-0.5">{unit}</span>
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface DistributionChartProps {
  /** Raw Monte Carlo sample vector */
  samples: number[];
  /** Chart title */
  title: string;
  /** Metric unit shown on axis and tooltip */
  unit?: string;
  /** Optional target/spec limit drawn as a vertical dashed line */
  target?: number;
  /** Target label (default "Target") */
  targetLabel?: string;
  /** Number of bins (default 20) */
  numBins?: number;
  /** Chart height in px */
  height?: number;
}

export const DistributionChart = memo(function DistributionChart({
  samples,
  title,
  unit = "",
  target,
  targetLabel = "Target",
  numBins = 20,
  height = 280,
}: DistributionChartProps) {
  const stats = useMemo(() => (samples.length ? computeStats(samples) : null), [samples]);
  const bins  = useMemo(
    () => (stats ? buildBins(samples, stats, numBins) : []),
    [samples, stats, numBins],
  );

  if (!stats) {
    return (
      <div className="
        rounded-2xl bg-slate-900 border border-slate-700 p-6
        text-slate-500 text-sm flex items-center justify-center
      " style={{ height }}>
        No distribution data available
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-700 p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-white">{title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {samples.length.toLocaleString()} Monte Carlo samples
          </p>
        </div>
        <ConfidenceIndicator cv={stats.cv} n={samples.length} showCV />
      </div>

      {/* Histogram */}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={bins} margin={{ top: 4, right: 16, bottom: 4, left: 0 }} barCategoryGap={1}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

          <XAxis
            dataKey="rangeLabel"
            tick={{ fill: "#64748b", fontSize: 9 }}
            tickLine={false}
            axisLine={{ stroke: "#1e293b" }}
            label={unit
              ? { value: unit, position: "insideBottomRight", offset: -4, fill: "#475569", fontSize: 10 }
              : undefined}
          />
          <YAxis
            tick={{ fill: "#64748b", fontSize: 9 }}
            tickLine={false}
            axisLine={false}
            width={28}
            label={{ value: "Count", angle: -90, position: "insideLeft", fill: "#475569", fontSize: 10 }}
          />

          <Tooltip content={<DistTooltip unit={unit} />} />

          {/* P5 / P95 region shading */}
          <ReferenceLine
            x={stats.p5.toFixed(1)}
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="3 2"
            label={{ value: `P5`, position: "insideBottomRight", fill: "#ef4444", fontSize: 9 }}
          />
          <ReferenceLine
            x={stats.p95.toFixed(1)}
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="3 2"
            label={{ value: `P95`, position: "insideBottomLeft", fill: "#ef4444", fontSize: 9 }}
          />
          <ReferenceLine
            x={stats.p50.toFixed(1)}
            stroke="#34d399"
            strokeWidth={1.5}
            label={{ value: `P50`, position: "insideTopRight", fill: "#34d399", fontSize: 9 }}
          />
          <ReferenceLine
            x={stats.mean.toFixed(1)}
            stroke="#94a3b8"
            strokeWidth={1.5}
            strokeDasharray="5 3"
            label={{ value: `Mean`, position: "insideTopLeft", fill: "#94a3b8", fontSize: 9 }}
          />

          {target !== undefined && (
            <ReferenceLine
              x={target.toFixed(1)}
              stroke="#818cf8"
              strokeWidth={2}
              strokeDasharray="4 2"
              label={{ value: targetLabel, position: "insideTopLeft", fill: "#818cf8", fontSize: 9 }}
            />
          )}

          <Bar dataKey="count" isAnimationActive={false} radius={[2, 2, 0, 0]}>
            {bins.map((bin, i) => (
              <Cell
                key={i}
                fill={bin.inCI ? "#10b981" : "#334155"}
                fillOpacity={bin.inCI ? 0.85 : 0.6}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Stat row */}
      <div className="grid grid-cols-5 gap-2">
        <StatPill label="P5"     value={stats.p5}   unit={unit} />
        <StatPill label="Median" value={stats.p50}  unit={unit} highlight />
        <StatPill label="Mean"   value={stats.mean} unit={unit} highlight />
        <StatPill label="P95"    value={stats.p95}  unit={unit} />
        <StatPill label="Std"    value={stats.std}  unit={unit} />
      </div>
    </div>
  );
});
