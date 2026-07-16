/**
 * packages/web/src/features/digital-twin/components/OperatingModeIndicator.tsx
 *
 * Colour-coded pill showing the current operating mode of the plant.
 */

import React, { memo } from "react";
import { OperatingMode } from "../types/twin";
import { MODE_LABELS, MODE_COLOURS } from "../utils/formatters";

interface OperatingModeIndicatorProps {
  mode: OperatingMode;
  className?: string;
}

export const OperatingModeIndicator = memo(function OperatingModeIndicator({
  mode,
  className = "",
}: OperatingModeIndicatorProps) {
  return (
    <span
      role="status"
      aria-label={`Operating mode: ${MODE_LABELS[mode]}`}
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full
        text-xs font-semibold uppercase tracking-wide
        ${MODE_COLOURS[mode]}
        ${className}
      `}
    >
      {MODE_LABELS[mode]}
    </span>
  );
});
