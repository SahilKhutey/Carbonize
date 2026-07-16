/**
 * packages/web/src/features/simulation-results/components/uncertainty/ConfidenceBand.tsx
 *
 * Time-series line chart with a shaded 90% confidence band (P5–P95).
 *
 * Visual language:
 *   - Solid emerald line  = median prediction
 *   - Green shaded area   = 90% CI band
 *   - Purple dashed line  = target / spec
 *   - Red dashed line     = actual observations (validation overlay)
 *   - Brush at bottom     = time-range zoom
 */

import React, { memo } from "react";
import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
  Legend, Brush, ResponsiveContainer,
} from "recharts";
import type { ConfidenceBandPoint } from "../../types/results";

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

function BandTooltip({
  active, payload, label, unit, showActual,
}: {
  active?: boolean; payload?: any[]; label?: string;
  unit: string; showActual: boolean;
}) {
  if (!active || !payload?.length) return null;
  const d: ConfidenceBandPoint = payload[0].payload;
  return (
    <div className="
      bg-slate-800 border border-slate-600 rounded-xl p-3
      text-xs text-slate-200 shadow-2xl
    ">
      <p className="font-semibold mb-2">{label}</p>
      <div className="space-y-1">
        <p>
          <span className="text-emerald-400 mr-1">●</span>
          Median:{" "}
          <span className="font-mono text-white font-bold">
            {d.median.toFixed(2)}{unit}
          </span>
        </p>
        <p className="text-slate-400">
          <span className="mr-1">▒</span>
          90% CI:{" "}
          <span className="font-mono">
            [{d.p5.toFixed(2)}, {d.p95.toFixed(2)}]{unit}
          </span>
        </p>
        <p className="text-slate-500 text-[10px]">
          Width: {(d.p95 - d.p5).toFixed(2)}{unit}
        </p>
        {showActual && d.actual !== undefined && (
          <p>
            <span className="text-red-400 mr-1">●</span>
            Actual:{" "}
            <span className="font-mono text-white">{d.actual.toFixed(2)}{unit}</span>
          </p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface ConfidenceBandChartProps {
  data: ConfidenceBandPoint[];
  title: string;
  unit?: string;
  xLabel?: string;
  /** Draw purple dashed line at this y value */
  target?: number;
  targetLabel?: string;
  showActual?: boolean;
  height?: number;
}

export const ConfidenceBandChart = memo(function ConfidenceBandChart({
  data,
  title,
  unit = "",
  xLabel,
  target,
  targetLabel = "Target",
  showActual = false,
  height = 280,
}: ConfidenceBandChartProps) {
  if (!data.length) {
    return (
      <div className="
        rounded-2xl bg-slate-900 border border-slate-700 p-6
        text-slate-500 text-sm flex items-center justify-center
      " style={{ height }}>
        No time-series data available
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-700 p-5 flex flex-col gap-3">
      {/* Header */}
      <div>
        <h3 className="text-sm font-bold text-white">{title}</h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Shaded region = 90% prediction interval
        </p>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 4, right: 24, bottom: xLabel ? 24 : 4, left: 0 }}
        >
          <defs>
            {/* Upper fill (P95 gradient) */}
            <linearGradient id="ciGradUpper" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.30} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.08} />
            </linearGradient>
            {/* Lower fill knocks out to white (trick to shade between P5 and P95) */}
            <linearGradient id="ciGradLower" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0f172a" stopOpacity={1} />
              <stop offset="100%" stopColor="#0f172a" stopOpacity={1} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />

          <XAxis
            dataKey="x"
            tick={{ fill: "#64748b", fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "#1e293b" }}
            label={xLabel
              ? { value: xLabel, position: "insideBottom", offset: -12, fill: "#475569", fontSize: 10 }
              : undefined}
          />
          <YAxis
            tick={{ fill: "#64748b", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            width={36}
            label={unit
              ? { value: unit, angle: -90, position: "insideLeft", fill: "#475569", fontSize: 10 }
              : undefined}
          />

          <Tooltip content={<BandTooltip unit={unit} showActual={showActual} />} />

          <Legend
            iconType="line"
            wrapperStyle={{ fontSize: 11, color: "#94a3b8" }}
          />

          {/* P95 fills down — creates the upper boundary of the shaded band */}
          <Area
            type="monotone"
            dataKey="p95"
            stroke="none"
            fill="url(#ciGradUpper)"
            name="90% CI upper"
            legendType="none"
            isAnimationActive={false}
          />

          {/* P5 fills back to bg — "erases" the bottom portion of the band */}
          <Area
            type="monotone"
            dataKey="p5"
            stroke="#10b981"
            strokeWidth={0.5}
            strokeDasharray="2 2"
            strokeOpacity={0.4}
            fill="url(#ciGradLower)"
            name="90% CI lower"
            legendType="none"
            isAnimationActive={false}
          />

          {/* Median line — most prominent */}
          <Area
            type="monotone"
            dataKey="median"
            stroke="#10b981"
            strokeWidth={2.5}
            fill="none"
            dot={false}
            activeDot={{ r: 4, fill: "#10b981" }}
            name="Median"
            isAnimationActive={false}
          />

          {/* Actual observations */}
          {showActual && (
            <Area
              type="monotone"
              dataKey="actual"
              stroke="#f87171"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              fill="none"
              dot={false}
              name="Actual"
              isAnimationActive={false}
            />
          )}

          {/* Target reference line */}
          {target !== undefined && (
            <ReferenceLine
              y={target}
              stroke="#818cf8"
              strokeWidth={1.5}
              strokeDasharray="5 3"
              label={{
                value: `${targetLabel}: ${target}${unit}`,
                position: "insideTopRight",
                fill: "#818cf8",
                fontSize: 10,
              }}
            />
          )}

          {/* Zoom brush */}
          <Brush
            dataKey="x"
            height={20}
            stroke="#334155"
            fill="#1e293b"
            travellerWidth={6}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});
