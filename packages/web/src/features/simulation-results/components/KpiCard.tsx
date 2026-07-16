/**
 * packages/web/src/features/simulation-results/components/KpiCard.tsx
 *
 * Enhanced KPI card for simulation results.
 *
 * Every card:
 *  - Shows mean value + unit
 *  - Shows ±CI badge (UncertaintyBadge) with popover explanation
 *  - Shows ConfidenceIndicator (HIGH / MED / LOW) in the top-right corner
 *  - Optionally shows an inline sparkline of the sample distribution
 *  - Status border (good/warning/critical) based on target comparison
 *  - Click triggers a drill-down callback (e.g. open DistributionChart modal)
 */

import React, { memo, useMemo } from "react";
import { TrendingUp, TrendingDown, Minus, ChevronRight } from "lucide-react";
import { UncertaintyBadge }    from "./uncertainty/UncertaintyBadge";
import { ConfidenceIndicator } from "./uncertainty/ConfidenceIndicator";
import { ci90HalfWidth }       from "../types/results";
import type { UQMetric }       from "../types/results";

// ---------------------------------------------------------------------------
// Sparkline (SVG — no Recharts, keeps card lightweight)
// ---------------------------------------------------------------------------

function Sparkline({ samples, target }: { samples: number[]; target?: number }) {
  const W = 120;
  const H = 28;

  const min = Math.min(...samples);
  const max = Math.max(...samples);
  const range = max - min || 1;

  // Down-sample to at most 60 points for perf
  const step = Math.max(1, Math.floor(samples.length / 60));
  const pts  = samples
    .filter((_, i) => i % step === 0)
    .map((s, i, arr) => {
      const x = (i / (arr.length - 1 || 1)) * W;
      const y = H - ((s - min) / range) * (H - 4) - 2;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const targetY = target !== undefined
    ? H - ((target - min) / range) * (H - 4) - 2
    : null;

  return (
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      aria-hidden
      className="opacity-60"
    >
      {/* P5–P95 band */}
      <rect x="0" y="4" width={W} height={H - 8} fill="#10b981" fillOpacity={0.06} />
      {/* Sparkline path */}
      <polyline
        fill="none"
        stroke="#34d399"
        strokeWidth="1.5"
        strokeLinejoin="round"
        points={pts}
      />
      {/* Target line */}
      {targetY !== null && (
        <line
          x1={0} y1={targetY} x2={W} y2={targetY}
          stroke="#818cf8"
          strokeWidth="0.75"
          strokeDasharray="2 2"
        />
      )}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Status border & background
// ---------------------------------------------------------------------------

type KpiStatus = "good" | "warning" | "critical" | "neutral";

function deriveStatus(mean: number, target?: number, lowIsGood?: boolean): KpiStatus {
  if (target === undefined) return "neutral";
  const ratio = mean / target;
  if (lowIsGood) {
    if (ratio <= 1.0) return "good";
    if (ratio <= 1.3) return "warning";
    return "critical";
  }
  if (ratio >= 0.95) return "good";
  if (ratio >= 0.80) return "warning";
  return "critical";
}

const STATUS_STYLES: Record<KpiStatus, string> = {
  good:     "border-l-4 border-l-emerald-500 bg-emerald-900/10",
  warning:  "border-l-4 border-l-amber-500   bg-amber-900/10",
  critical: "border-l-4 border-l-red-500     bg-red-900/10",
  neutral:  "border-l-4 border-l-slate-600   bg-slate-800/30",
};

// ---------------------------------------------------------------------------
// Trend icon
// ---------------------------------------------------------------------------

const TREND_ICON: Record<string, React.ReactNode> = {
  up:   <TrendingUp   className="w-3.5 h-3.5" aria-hidden />,
  down: <TrendingDown className="w-3.5 h-3.5" aria-hidden />,
  flat: <Minus        className="w-3.5 h-3.5" aria-hidden />,
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface KpiCardProps {
  /** Card title */
  label: string;
  /** UQ metric — has mean, cv, p5, p95, samples etc. */
  metric: UQMetric;
  /** Display unit (e.g. "%" or " MPa") */
  unit?: string;
  /** Number of decimal places for the main value */
  precision?: number;
  /** Optional spec limit to compare against */
  target?: number;
  /** If true, lower values = better (e.g. emissions) */
  lowIsGood?: boolean;
  /** Trend direction and label for period-over-period comparison */
  trend?: "up" | "down" | "flat";
  trendLabel?: string;
  /** Show mini sparkline — only for cards with samples */
  showSparkline?: boolean;
  /** Click handler — e.g. open distribution modal */
  onClick?: () => void;
}

export const KpiCard = memo(function KpiCard({
  label,
  metric,
  unit = "",
  precision = 1,
  target,
  lowIsGood = false,
  trend,
  trendLabel,
  showSparkline = true,
  onClick,
}: KpiCardProps) {
  const status = useMemo(
    () => deriveStatus(metric.mean, target, lowIsGood),
    [metric.mean, target, lowIsGood],
  );

  const halfWidth = useMemo(() => ci90HalfWidth(metric), [metric]);
  const hasSamples = metric.samples.length > 0;

  return (
    <div
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={onClick ? (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      } : undefined}
      className={`
        group relative w-full text-left
        rounded-2xl p-5
        bg-slate-900 border border-slate-700
        ${STATUS_STYLES[status]}
        ${onClick ? "hover:border-slate-500 cursor-pointer" : "cursor-default"}
        transition-all shadow-lg
        focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500
      `}
      aria-label={`${label}: ${metric.mean.toFixed(precision)}${unit}, ±${halfWidth.toFixed(1)}${unit} 90% CI`}
    >
      {/* Confidence pill — top right */}
      <div className="absolute top-3 right-3">
        <ConfidenceIndicator cv={metric.cv} size="sm" />
      </div>

      {/* Label */}
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 pr-20">
        {label}
      </p>

      {/* Main value + uncertainty badge */}
      <div className="flex items-baseline gap-2 flex-wrap">
        <span className="text-3xl font-black text-white tabular-nums leading-none">
          {metric.mean.toFixed(precision)}
        </span>
        <span className="text-sm text-slate-500">{unit}</span>
        <UncertaintyBadge
          ci90HalfWidth={halfWidth}
          unit={unit}
          cv={metric.cv}
          size="sm"
        />
      </div>

      {/* Target comparison */}
      {target !== undefined && (
        <p className="text-[11px] text-slate-500 mt-1.5">
          Target: <span className="text-slate-300 font-semibold">{target}{unit}</span>
          {status === "good"     && <span className="text-emerald-400 ml-2">✓ Met</span>}
          {status === "warning"  && <span className="text-amber-400   ml-2">⚠ Below</span>}
          {status === "critical" && <span className="text-red-400     ml-2">✗ Critical</span>}
        </p>
      )}

      {/* Trend */}
      {trend && (
        <p className={`
          flex items-center gap-1 text-[11px] mt-1 font-semibold
          ${trend === "up"   ? "text-emerald-400" :
            trend === "down" ? "text-red-400"     :
                               "text-slate-500"}
        `}>
          {TREND_ICON[trend]}
          {trendLabel}
        </p>
      )}

      {/* Sparkline */}
      {showSparkline && hasSamples && (
        <div className="mt-3">
          <Sparkline samples={metric.samples} target={target} />
        </div>
      )}

      {/* Drill-down arrow */}
      {onClick && (
        <ChevronRight
          className="
            absolute bottom-4 right-3
            w-4 h-4 text-slate-600
            group-hover:text-slate-400 transition-colors
          "
          aria-hidden
        />
      )}
    </div>
  );
});
