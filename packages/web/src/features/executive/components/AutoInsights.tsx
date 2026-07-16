/**
 * packages/web/src/features/executive/components/AutoInsights.tsx
 *
 * AI-generated anomaly and opportunity cards.
 */

import React, { memo } from "react";
import { AlertCircle, TrendingUp, Info } from "lucide-react";
import type { AutoInsight } from "../types/executive";
import { useNavigate } from "react-router-dom";

const SEV_CFG = {
  warning: {
    icon: <AlertCircle className="w-4 h-4" aria-hidden />,
    border: "border-amber-700/50",
    bg: "bg-amber-900/20",
    text: "text-amber-300",
    badge: "bg-amber-800 text-amber-200",
    label: "Warning",
  },
  opportunity: {
    icon: <TrendingUp className="w-4 h-4" aria-hidden />,
    border: "border-emerald-700/50",
    bg: "bg-emerald-900/20",
    text: "text-emerald-300",
    badge: "bg-emerald-800 text-emerald-200",
    label: "Opportunity",
  },
  info: {
    icon: <Info className="w-4 h-4" aria-hidden />,
    border: "border-sky-700/50",
    bg: "bg-sky-900/20",
    text: "text-sky-300",
    badge: "bg-sky-800 text-sky-200",
    label: "Info",
  },
};

interface AutoInsightsProps {
  insights: AutoInsight[];
}

export const AutoInsights = memo(function AutoInsights({ insights }: AutoInsightsProps) {
  const navigate = useNavigate();
  if (insights.length === 0) return null;

  return (
    <section aria-label="Auto-generated insights">
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
        💡 Insights
      </h2>
      <div className="space-y-3">
        {insights.map((insight) => {
          const cfg = SEV_CFG[insight.severity];
          return (
            <div
              key={insight.id}
              className={`
                p-4 rounded-xl border ${cfg.border} ${cfg.bg}
                flex items-start gap-3
              `}
            >
              <span className={`${cfg.text} shrink-0 mt-0.5`}>{cfg.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-start gap-2 flex-wrap">
                  <p className="text-sm font-semibold text-slate-100">{insight.title}</p>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${cfg.badge}`}>
                    {cfg.label}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{insight.summary}</p>
                <p className="text-xs text-slate-600 mt-0.5">{insight.plantName}</p>
                {insight.drillDownUrl && (
                  <button
                    onClick={() => navigate(insight.drillDownUrl!)}
                    className="mt-2 text-xs font-semibold text-emerald-400 hover:text-emerald-300 underline underline-offset-2 transition-colors"
                  >
                    Drill Down →
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
});
