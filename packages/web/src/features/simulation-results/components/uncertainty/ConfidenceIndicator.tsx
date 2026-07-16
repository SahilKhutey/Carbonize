/**
 * packages/web/src/features/simulation-results/components/uncertainty/ConfidenceIndicator.tsx
 *
 * HIGH / MEDIUM / LOW confidence pill computed from the coefficient of variation.
 * Used in chart headers so users instantly know how much to trust a prediction.
 *
 * CV < 0.10  → HIGH    (tight band, reliable)
 * CV < 0.25  → MEDIUM  (moderate uncertainty, treat as estimate)
 * CV ≥ 0.25  → LOW     (wide band, speculative)
 */

import React, { memo } from "react";
import { CheckCircle, AlertTriangle, AlertCircle } from "lucide-react";
import type { ConfidenceLevel } from "../../types/results";
import { classifyConfidence } from "../../types/results";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const LEVEL_CFG: Record<ConfidenceLevel, {
  label: string;
  description: string;
  icon: React.ReactNode;
  pill: string;
  dot: string;
}> = {
  HIGH: {
    label: "High confidence",
    description: "Tight CI — predictions are reliable",
    icon: <CheckCircle className="w-3.5 h-3.5" aria-hidden />,
    pill: "bg-emerald-900/40 border-emerald-600 text-emerald-300",
    dot: "bg-emerald-400",
  },
  MEDIUM: {
    label: "Medium confidence",
    description: "Moderate CI — treat as estimates",
    icon: <AlertTriangle className="w-3.5 h-3.5" aria-hidden />,
    pill: "bg-amber-900/40 border-amber-600 text-amber-300",
    dot: "bg-amber-400",
  },
  LOW: {
    label: "Low confidence",
    description: "Wide CI — predictions are speculative",
    icon: <AlertCircle className="w-3.5 h-3.5" aria-hidden />,
    pill: "bg-red-900/40 border-red-600 text-red-300",
    dot: "bg-red-400",
  },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface ConfidenceIndicatorProps {
  /** Coefficient of variation (std / |mean|) */
  cv: number;
  /** Sample count for context */
  n?: number;
  /** Controls whether to show CV value inline */
  showCV?: boolean;
  /** Size variant */
  size?: "sm" | "md";
}

export const ConfidenceIndicator = memo(function ConfidenceIndicator({
  cv,
  n,
  showCV = false,
  size = "sm",
}: ConfidenceIndicatorProps) {
  const level = classifyConfidence(cv);
  const cfg   = LEVEL_CFG[level];

  const sizeClass = size === "sm"
    ? "text-[10px] px-1.5 py-0.5 gap-1"
    : "text-xs px-2 py-1 gap-1.5";

  return (
    <span
      role="status"
      aria-label={`${cfg.label}: ${cfg.description}`}
      className={`
        inline-flex items-center border rounded-full font-semibold
        select-none
        ${sizeClass} ${cfg.pill}
      `}
      title={`${cfg.label} — CV=${cv.toFixed(3)}${n ? `, n=${n}` : ""}`}
    >
      {cfg.icon}
      {level}
      {showCV && (
        <span className="opacity-60 font-mono ml-0.5">
          {(cv * 100).toFixed(1)}%
        </span>
      )}
    </span>
  );
});
