/**
 * packages/web/src/features/simulation-results/components/uncertainty/UncertaintyBadge.tsx
 *
 * Inline "±X unit" badge that appears beside any point estimate to remind
 * users that predictions carry uncertainty. Clicking opens an explanatory popover.
 *
 * Usage:
 *   CO₂ Capture: 87.2%
 *   <UncertaintyBadge ci90HalfWidth={6.7} unit="%" cv={0.077} />
 */

import React, { memo, useState, useRef, useEffect } from "react";
import { Info } from "lucide-react";
import { classifyConfidence } from "../../types/results";
import type { ConfidenceLevel } from "../../types/results";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const BADGE_STYLE: Record<ConfidenceLevel, string> = {
  HIGH:   "bg-emerald-900/40 border-emerald-600 text-emerald-300 hover:bg-emerald-800/60",
  MEDIUM: "bg-amber-900/40   border-amber-600   text-amber-300   hover:bg-amber-800/60",
  LOW:    "bg-red-900/40     border-red-600     text-red-300     hover:bg-red-800/60",
};

const POPOVER_TEXT: Record<ConfidenceLevel, string> = {
  HIGH:   "Tight uncertainty band. The prediction is reliable — measurements confirm a narrow range.",
  MEDIUM: "Moderate uncertainty. Treat this as an estimate. Further experimental validation is recommended.",
  LOW:    "Wide uncertainty band. The prediction is speculative. Critical experiments should be conducted before relying on this value.",
};

// ---------------------------------------------------------------------------
// Popover (self-contained, no library dependency)
// ---------------------------------------------------------------------------

interface PopoverProps {
  ci90HalfWidth: number;
  unit: string;
  cv?: number;
  level: ConfidenceLevel;
  onClose: () => void;
  anchorRef: React.RefObject<HTMLButtonElement | null>;
}

function UncertaintyPopover({ ci90HalfWidth, unit, cv, level, onClose, anchorRef }: PopoverProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node) &&
          anchorRef.current && !anchorRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    window.addEventListener("keydown", handleKey);
    document.addEventListener("mousedown", handleClick);
    return () => {
      window.removeEventListener("keydown", handleKey);
      document.removeEventListener("mousedown", handleClick);
    };
  }, [onClose, anchorRef]);

  return (
    <div
      ref={ref}
      role="dialog"
      aria-modal="false"
      aria-label="Uncertainty explanation"
      className="
        absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2
        w-72 p-4 rounded-xl
        bg-slate-800 border border-slate-600
        shadow-2xl text-sm text-slate-200
      "
    >
      {/* Arrow */}
      <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-slate-800 border-r border-b border-slate-600 rotate-45" />

      <p className="font-bold text-white mb-2">90% Confidence Interval</p>
      <p className="text-slate-300 text-xs leading-relaxed">
        The true value lies within{" "}
        <span className="font-mono text-emerald-300">
          ±{ci90HalfWidth.toFixed(1)}{unit}
        </span>{" "}
        of this prediction with 90% probability.
      </p>

      {cv !== undefined && (
        <div className="mt-2 flex items-center gap-2">
          <span className="text-xs text-slate-400">
            Coefficient of variation:{" "}
            <span className="font-mono text-slate-200">{(cv * 100).toFixed(1)}%</span>
          </span>
        </div>
      )}

      <div className={`
        mt-3 px-2 py-1.5 rounded-lg text-xs
        ${level === "HIGH"   ? "bg-emerald-900/60 text-emerald-200" :
          level === "MEDIUM" ? "bg-amber-900/60   text-amber-200"   :
                               "bg-red-900/60     text-red-200"}
      `}>
        {POPOVER_TEXT[level]}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Badge
// ---------------------------------------------------------------------------

interface UncertaintyBadgeProps {
  ci90HalfWidth: number;
  unit?: string;
  cv?: number;
  size?: "sm" | "md" | "lg";
  /** If provided, popover contains a "View distribution" link */
  onDrillDown?: () => void;
}

export const UncertaintyBadge = memo(function UncertaintyBadge({
  ci90HalfWidth,
  unit = "",
  cv,
  size = "md",
  onDrillDown,
}: UncertaintyBadgeProps) {
  const [open, setOpen] = useState(false);
  const btnRef = useRef<HTMLButtonElement>(null);

  const level: ConfidenceLevel = cv !== undefined
    ? classifyConfidence(cv)
    : "MEDIUM";

  const sizeClass = {
    sm: "text-[10px] px-1.5 py-0.5 gap-0.5",
    md: "text-xs px-2 py-0.5 gap-1",
    lg: "text-sm px-2.5 py-1 gap-1",
  }[size];

  return (
    <span className="relative inline-flex">
      <button
        ref={btnRef}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-label={`Uncertainty: ±${ci90HalfWidth.toFixed(1)}${unit} (90% CI). Click for details.`}
        className={`
          inline-flex items-center border rounded-full font-semibold
          transition-colors cursor-pointer
          ${sizeClass} ${BADGE_STYLE[level]}
        `}
      >
        ±{ci90HalfWidth.toFixed(1)}{unit}
        <Info className="w-3 h-3 opacity-70" aria-hidden />
      </button>

      {open && (
        <UncertaintyPopover
          ci90HalfWidth={ci90HalfWidth}
          unit={unit}
          cv={cv}
          level={level}
          onClose={() => setOpen(false)}
          anchorRef={btnRef}
        />
      )}
    </span>
  );
});
