/**
 * packages/web/src/features/executive/components/PortfolioKPIs.tsx
 *
 * 6 hero KPI cards with period-over-period trend arrows.
 * Executive BI aesthetic — spacious, clean, professional.
 */

import React, { memo } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { PortfolioSummary } from "../types/executive";

interface PortfolioKPIsProps {
  data: PortfolioSummary;
}

function TrendArrow({ pct, trend }: { pct: number; trend: "up" | "down" | "flat" }) {
  const isPositive = pct > 0;
  const cls = isPositive ? "text-emerald-400" : pct < 0 ? "text-red-400" : "text-slate-500";
  return (
    <span className={`flex items-center gap-0.5 text-xs font-semibold ${cls}`} aria-label={`${pct > 0 ? "+" : ""}${pct.toFixed(1)}% trend`}>
      {trend === "up"   && <TrendingUp   className="w-3 h-3" aria-hidden />}
      {trend === "down" && <TrendingDown className="w-3 h-3" aria-hidden />}
      {trend === "flat" && <Minus        className="w-3 h-3" aria-hidden />}
      {pct > 0 && "+"}{pct.toFixed(1)}%
    </span>
  );
}

export const PortfolioKPIs = memo(function PortfolioKPIs({ data }: PortfolioKPIsProps) {
  return (
    <section aria-label="Portfolio KPIs">
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4">
        {data.kpis.map((kpi) => (
          <div
            key={kpi.id}
            className="
              bg-slate-800/50 border border-slate-700/50
              rounded-2xl p-5
              flex flex-col gap-1
              hover:border-slate-600 transition-colors
            "
          >
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest truncate">
              {kpi.label}
            </p>
            <p className="text-2xl font-black text-white tabular-nums leading-tight">
              {kpi.value}
              {kpi.unit && (
                <span className="text-xs font-medium text-slate-500 ml-1">{kpi.unit}</span>
              )}
            </p>
            {kpi.periodLabel && (
              <p className="text-xs text-slate-600">{kpi.periodLabel}</p>
            )}
            {kpi.changePct !== 0 && (
              <TrendArrow pct={kpi.changePct} trend={kpi.trend} />
            )}
          </div>
        ))}
      </div>
    </section>
  );
});
