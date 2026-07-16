/**
 * packages/web/src/features/digital-twin/utils/formatters.ts
 *
 * Pure formatting utilities for Digital Twin display values.
 */

import { OperatingMode } from "../types/twin";

/** Format seconds into "Xh Ym" or "Zm" */
export function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h === 0) return `${m}m`;
  return `${h}h ${m}m`;
}

/** Format a numeric value with a fixed number of decimal places */
export function fmt(value: number | null | undefined, decimals = 1, fallback = "—"): string {
  if (value == null || !isFinite(value)) return fallback;
  return value.toFixed(decimals);
}

/** Human-readable label for an OperatingMode */
export const MODE_LABELS: Record<OperatingMode, string> = {
  idle:        "Idle",
  starting:    "Starting…",
  running:     "Running",
  stopping:    "Stopping…",
  fault:       "⚠ Fault",
  maintenance: "Maintenance",
};

/** Tailwind colour token for each OperatingMode pill */
export const MODE_COLOURS: Record<OperatingMode, string> = {
  idle:        "bg-slate-700 text-slate-300",
  starting:    "bg-amber-700 text-amber-100",
  running:     "bg-emerald-700 text-emerald-100",
  stopping:    "bg-amber-700 text-amber-100",
  fault:       "bg-red-700 text-red-100",
  maintenance: "bg-indigo-700 text-indigo-100",
};

/** ISO timestamp → "HH:MM:SS" local time */
export function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString("en-IN", { hour12: false });
  } catch {
    return iso;
  }
}

/** epoch ms → "HH:MM:SS" local time (used in charts) */
export function epochToTimeStr(ms: number): string {
  return new Date(ms).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}
