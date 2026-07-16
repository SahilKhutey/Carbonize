/**
 * packages/web/src/features/simulation-results/components/uncertainty/SobolTornadoChart.tsx
 *
 * Horizontal tornado chart showing Sobol sensitivity indices.
 *
 * Layout:
 *   Parameter label | ████████░░ | S₁ value | S_T value
 *
 * Bars:
 *   - Dark emerald bar  = first-order index S₁ (direct effect)
 *   - Light emerald bar = total-order index S_T (including interactions)
 *   - Gap between them  = interaction effect (S_T − S₁)
 *
 * Interaction bar is rendered as a separate translucent segment on top.
 *
 * Also shows:
 *   - "Critical experiments" ranked list
 *   - Variance explained summary ("Top N parameters explain X% of uncertainty")
 *   - 10% significance threshold dashed line
 */

import React, { useMemo, memo, useState } from "react";
import {
  BarChart, Bar, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
  ResponsiveContainer, LabelList,
} from "recharts";
import { AlertCircle, ChevronRight, Info } from "lucide-react";
import type { SobolIndex } from "../../types/results";

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

function SobolTooltip({ active, payload }: { active?: boolean; payload?: any[] }) {
  if (!active || !payload?.length) return null;
  const d: SobolIndex = payload[0].payload;
  const interaction = d.st - d.s1;

  return (
    <div className="
      bg-slate-800 border border-slate-600 rounded-xl p-3
      text-xs text-slate-200 shadow-2xl w-64
    ">
      <p className="font-bold font-mono text-white mb-2">{d.label}</p>
      <div className="space-y-1.5">
        <div className="flex justify-between">
          <span className="text-emerald-400">S₁ (first-order)</span>
          <span className="font-mono font-bold text-white">{(d.s1 * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-emerald-300/60">S_T (total-order)</span>
          <span className="font-mono font-bold text-white">{(d.st * 100).toFixed(1)}%</span>
        </div>
        {interaction > 0.005 && (
          <div className="flex justify-between text-slate-400">
            <span>Interaction effect</span>
            <span className="font-mono">{(interaction * 100).toFixed(1)}%</span>
          </div>
        )}
        {d.current_uncertainty && (
          <div className="mt-2 pt-2 border-t border-slate-700 text-slate-400">
            Current uncertainty: {d.current_uncertainty}
          </div>
        )}
        {d.unit && (
          <div className="text-slate-500">Units: {d.unit}</div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

interface SobolTornadoChartProps {
  indices: SobolIndex[];
  outputName: string;
  outputUnit?: string;
  /** Max parameters to show (rest collapsed) */
  maxShown?: number;
  height?: number;
  /** Called when user clicks a parameter row in the critical experiments list */
  onParameterClick?: (parameter: string) => void;
}

export const SobolTornadoChart = memo(function SobolTornadoChart({
  indices,
  outputName,
  outputUnit = "",
  maxShown = 10,
  height,
  onParameterClick,
}: SobolTornadoChartProps) {
  const [showAll, setShowAll] = useState(false);

  // Sort descending by S_T
  const sorted = useMemo(
    () => [...indices].sort((a, b) => b.st - a.st),
    [indices],
  );

  const displayed = showAll ? sorted : sorted.slice(0, maxShown);

  // Variance attribution summary
  const top5 = sorted.slice(0, 5);
  const top5ST = top5.reduce((s, p) => s + p.st, 0);

  // Dynamic chart height based on number of rows
  const chartHeight = height ?? Math.max(180, displayed.length * 40 + 60);

  // xAxis domain: round up to next 0.1
  const maxST = sorted[0]?.st ?? 0.5;
  const xMax = Math.min(1, Math.ceil(maxST * 10) / 10 + 0.1);

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-700 p-5 flex flex-col gap-5">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-bold text-white">Sensitivity Analysis</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Which parameters most affect{" "}
            <span className="text-emerald-300 font-mono font-semibold">
              {outputName}{outputUnit ? ` (${outputUnit})` : ""}
            </span>?
          </p>
        </div>
        <div className="flex items-center gap-1 text-[10px] text-slate-500 border border-slate-700 rounded-full px-2 py-1">
          <Info className="w-3 h-3" aria-hidden />
          Sobol method
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-[11px] text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm bg-emerald-600" />
          S₁ — Direct effect
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm bg-emerald-400/30 border border-emerald-500" />
          S_T − S₁ — Interactions
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block w-6 border-t border-dashed border-red-500 mt-0.5" />
          10% threshold
        </span>
      </div>

      {/* Tornado chart */}
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          data={displayed}
          layout="vertical"
          margin={{ top: 4, right: 56, bottom: 4, left: 0 }}
          barCategoryGap="25%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />

          <XAxis
            type="number"
            domain={[0, xMax]}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            tick={{ fill: "#64748b", fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "#1e293b" }}
          />
          <YAxis
            dataKey="label"
            type="category"
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={130}
          />

          <Tooltip content={<SobolTooltip />} />

          {/* 10% significance threshold */}
          <ReferenceLine
            x={0.10}
            stroke="#ef4444"
            strokeDasharray="3 2"
            strokeWidth={1}
            label={{
              value: "10%",
              position: "insideTopRight",
              fill: "#ef4444",
              fontSize: 9,
            }}
          />

          {/* S_T bar (lighter — behind S1 bar) */}
          <Bar
            dataKey="st"
            name="Total-order S_T"
            isAnimationActive={false}
            radius={[0, 3, 3, 0]}
            fill="#10b981"
            fillOpacity={0.25}
          >
            {/* S_T value label */}
            <LabelList
              dataKey="st"
              position="right"
              formatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              style={{ fill: "#64748b", fontSize: 9 }}
            />
          </Bar>

          {/* S1 bar (darker — overlaid on top of S_T) */}
          <Bar
            dataKey="s1"
            name="First-order S₁"
            isAnimationActive={false}
            radius={[0, 2, 2, 0]}
          >
            {displayed.map((entry, i) => {
              const rank = sorted.indexOf(entry);
              // Green gradient by rank: top = bright, lower = dimmer
              const opacity = 1 - (rank / sorted.length) * 0.5;
              return (
                <Cell
                  key={i}
                  fill="#059669"
                  fillOpacity={opacity}
                  onClick={() => onParameterClick?.(entry.parameter)}
                  style={{ cursor: onParameterClick ? "pointer" : "default" }}
                />
              );
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {sorted.length > maxShown && (
        <button
          onClick={() => setShowAll((s) => !s)}
          className="text-xs text-emerald-400 hover:text-emerald-300 self-center transition-colors"
        >
          {showAll ? "Show fewer ↑" : `Show all ${sorted.length} parameters ↓`}
        </button>
      )}

      {/* Variance summary box */}
      <div className="
        p-3 rounded-xl
        bg-amber-900/20 border border-amber-700/50
        flex items-start gap-2.5
      ">
        <AlertCircle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" aria-hidden />
        <div>
          <p className="text-sm font-semibold text-amber-200">
            Top 5 parameters explain{" "}
            <span className="text-amber-300">{(top5ST * 100).toFixed(0)}%</span>{" "}
            of total output uncertainty
          </p>
          <p className="text-xs text-amber-400/80 mt-1">
            Validating these experimentally would most efficiently reduce prediction uncertainty.
          </p>
        </div>
      </div>

      {/* Critical experiments ranked list */}
      <div>
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
          Recommended critical experiments (highest to lowest impact)
        </p>
        <ol className="space-y-1" aria-label="Critical experiments">
          {top5.map((p, i) => (
            <li
              key={p.parameter}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg text-xs
                bg-slate-800/50 border border-slate-700/50
                ${onParameterClick ? "cursor-pointer hover:bg-slate-700/60 hover:border-slate-600 transition-colors" : ""}
              `}
              onClick={() => onParameterClick?.(p.parameter)}
              aria-label={`Critical experiment ${i + 1}: ${p.label}, total sensitivity ${(p.st * 100).toFixed(1)}%`}
            >
              <span className="text-slate-500 tabular-nums w-4 shrink-0">{i + 1}.</span>
              <span className="font-mono text-slate-200 flex-1 truncate">{p.label}</span>
              {p.current_uncertainty && (
                <span className="text-slate-500 hidden sm:inline shrink-0">{p.current_uncertainty}</span>
              )}
              <span className="text-emerald-400 font-semibold tabular-nums shrink-0">
                {(p.st * 100).toFixed(1)}%
              </span>
              {onParameterClick && (
                <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" aria-hidden />
              )}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
});
