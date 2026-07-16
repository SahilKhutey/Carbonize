/**
 * KPI card with touch-friendly sizing and accessibility.
 * 
 * Mobile targets must be ≥ 44x44px (WCAG 2.5.5)
 * Tablet touch targets: 48-56px recommended
 * 
 * Font sizes:
 * - mobile: 14px minimum
 * - tablet: 16px
 * - desktop: 16px
 */

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { UncertaintyBadge } from "../../features/simulation-results/components/uncertainty/UncertaintyBadge";
import { cn } from "../../lib/utils";

interface AccessibleKpiCardProps {
  label: string;
  value: number;
  unit?: string;
  ci90HalfWidth?: number;
  trend?: "up" | "down" | "flat";
  trendValue?: string;
  target?: number;
  status?: "good" | "warning" | "critical" | "neutral";
  /** Optional detailed description for screen readers */
  detailedDescription?: string;
  /** Click handler */
  onClick?: () => void;
}

const STATUS_STYLES: Record<NonNullable<AccessibleKpiCardProps["status"]>, string> = {
  good: "border-l-emerald-500 bg-emerald-900/10",
  warning: "border-l-amber-500 bg-amber-900/10",
  critical: "border-l-red-500 bg-red-900/10",
  neutral: "border-l-slate-600 bg-slate-800/30",
};

export function AccessibleKpiCard({
  label, value, unit = "",
  ci90HalfWidth, trend, trendValue, target, status = "neutral",
  detailedDescription, onClick,
}: AccessibleKpiCardProps) {
  const statusClass = STATUS_STYLES[status];
  
  // Build accessible label for screen readers
  const ariaLabel = [
    label,
    `value: ${value.toFixed(1)}${unit}`,
    ci90HalfWidth !== undefined ? `plus or minus ${ci90HalfWidth.toFixed(1)}${unit}` : "",
    target !== undefined ? `target: ${target}${unit}` : "",
    detailedDescription,
  ].filter(Boolean).join(", ");
  
  return (
    <Card
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={ariaLabel}
      onClick={onClick}
      onKeyDown={onClick ? (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      } : undefined}
      className={cn(
        "border-l-4 transition-all bg-slate-900 border-slate-700",
        statusClass,
        // Touch target: WCAG 2.5.5 Level AAA requires 44x44 minimum
        "min-h-[88px]",     // 2x tap target height
        onClick && "cursor-pointer hover:border-slate-500 hover:shadow-md active:scale-[0.99]",
        // Focus visible
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-emerald-500 focus-visible:outline-offset-2"
      )}
    >
      <CardContent className="p-3 sm:p-4">
        {/* Label with sufficient contrast and size */}
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
          {label}
        </p>
        
        {/* Value + unit (large, high contrast) */}
        <div className="flex items-baseline gap-1 flex-wrap">
          <span className="text-2xl sm:text-3xl font-bold text-white tabular-nums">
            {value.toFixed(1)}
          </span>
          {unit && (
            <span className="text-sm text-slate-400">{unit}</span>
          )}
          {ci90HalfWidth !== undefined && (
            <UncertaintyBadge
              ci90HalfWidth={ci90HalfWidth}
              unit={unit}
              size="sm"
            />
          )}
        </div>
        
        {/* Trend / target (smaller text) */}
        {(trend || target !== undefined) && (
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-400">
            {trend === "up" && <TrendingUp className="w-3 h-3" aria-hidden="true" />}
            {trend === "down" && <TrendingDown className="w-3 h-3" aria-hidden="true" />}
            {trend === "flat" && <Minus className="w-3 h-3" aria-hidden="true" />}
            <span>{trendValue}</span>
            {target !== undefined && <span>Target: {target}{unit}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
