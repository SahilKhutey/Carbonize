/**
 * packages/web/src/features/operator/components/SensorDetail.tsx
 *
 * Slide-in drill-down panel for a single sensor metric.
 * Shows: current value, 1-hour rolling trend chart, status, setpoint.
 * Triggered by clicking a KPI tile or schematic sensor tag.
 */

import React, { memo } from "react";
import { X } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { SensorHistoryPoint } from "../../digital-twin/types/twin";
import { epochToTimeStr } from "../../digital-twin/utils/formatters";

// ---------------------------------------------------------------------------
// Metric display config
// ---------------------------------------------------------------------------

interface MetricCfg {
  label: string;
  unit: string;
  colour: string;
  normalMin?: number;
  normalMax?: number;
  alarmHigh?: number;
}

const METRIC_CFG: Record<string, MetricCfg> = {
  co2_outlet_pct:     { label: "CO₂ Outlet",      unit: "%",        colour: "#34d399", normalMin: 0,   normalMax: 3,   alarmHigh: 5   },
  so2_outlet_mg_nm3:  { label: "SO₂ Outlet",       unit: "mg/Nm³",   colour: "#fb923c", normalMin: 0,   normalMax: 200, alarmHigh: 300 },
  mesh_dp_mmH2O:      { label: "Mesh ΔP",           unit: "mmH₂O",   colour: "#a78bfa", normalMin: 0,   normalMax: 200, alarmHigh: 240 },
  reactor_temp_c:     { label: "Reactor Temp",      unit: "°C",       colour: "#f87171", normalMin: 35,  normalMax: 45,  alarmHigh: 55  },
  pH:                 { label: "pH",                unit: "",         colour: "#4ade80", normalMin: 8,   normalMax: 9              },
  flow_nm3_hr:        { label: "Gas Flow",          unit: "Nm³/hr",   colour: "#38bdf8"                                             },
  co2_capture_pct:    { label: "CO₂ Capture",       unit: "%",        colour: "#60a5fa", normalMin: 80                              },
  so2_capture_pct:    { label: "SO₂ Capture",       unit: "%",        colour: "#fbbf24", normalMin: 90                              },
  co2_inlet_pct:      { label: "CO₂ Inlet",         unit: "%",        colour: "#94a3b8"                                             },
  so2_inlet_mg_nm3:   { label: "SO₂ Inlet",         unit: "mg/Nm³",   colour: "#94a3b8"                                             },
};

const DEFAULT_CFG: MetricCfg = { label: "Sensor", unit: "", colour: "#94a3b8" };

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface SensorDetailProps {
  metricId: string;
  currentValue?: number | null;
  history: SensorHistoryPoint[];
  onClose: () => void;
  maxPoints?: number;
}

export const SensorDetail = memo(function SensorDetail({
  metricId,
  currentValue,
  history,
  onClose,
  maxPoints = 60,
}: SensorDetailProps) {
  const cfg = METRIC_CFG[metricId] ?? DEFAULT_CFG;

  const chartData = history.slice(-maxPoints).map((pt) => ({
    time: epochToTimeStr(pt.timestamp),
    value: (pt.readings as Record<string, number | undefined>)[metricId] ?? null,
  })).filter((d) => d.value != null);

  const latest = currentValue ?? chartData.at(-1)?.value ?? null;

  const isAlarming =
    cfg.alarmHigh != null && latest != null && latest >= cfg.alarmHigh;
  const isWarning =
    !isAlarming &&
    cfg.normalMax != null && latest != null && latest >= cfg.normalMax;

  const valueColour = isAlarming
    ? "text-red-400"
    : isWarning
    ? "text-amber-400"
    : "text-emerald-400";

  return (
    /* Overlay backdrop */
    <div
      className="fixed inset-0 z-40 flex justify-end"
      role="dialog"
      aria-modal="true"
      aria-label={`Sensor detail: ${cfg.label}`}
    >
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden
      />

      {/* Panel */}
      <div className="
        relative z-10 w-full max-w-md h-full
        bg-slate-900 border-l border-slate-700
        flex flex-col overflow-hidden
        shadow-2xl
      ">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700">
          <div>
            <h2 className="text-base font-bold text-white">{cfg.label}</h2>
            {cfg.normalMin != null && cfg.normalMax != null && (
              <p className="text-xs text-slate-500 mt-0.5">
                Normal range: {cfg.normalMin}–{cfg.normalMax} {cfg.unit}
              </p>
            )}
            {cfg.alarmHigh != null && (
              <p className="text-xs text-red-500 mt-0.5">
                Alarm threshold: {cfg.alarmHigh} {cfg.unit}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Close sensor detail"
          >
            <X className="w-4 h-4 text-slate-400" aria-hidden />
          </button>
        </div>

        {/* Current value hero */}
        <div className="px-5 py-6 border-b border-slate-700/50">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Current</p>
          <p className={`text-5xl font-black tabular-nums mt-1 ${valueColour}`}>
            {latest != null ? latest.toFixed(cfg.unit === "%" ? 2 : 0) : "—"}
            <span className="text-lg font-medium text-slate-500 ml-2">{cfg.unit}</span>
          </p>
          {isAlarming && (
            <p className="text-xs text-red-400 font-semibold mt-2">⚠ Above alarm threshold</p>
          )}
          {isWarning && (
            <p className="text-xs text-amber-400 font-semibold mt-2">⚠ Above normal range</p>
          )}
        </div>

        {/* Trend chart */}
        <div className="flex-1 px-4 py-4 flex flex-col">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
            Last {Math.min(chartData.length, maxPoints)} readings
          </p>
          {chartData.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-slate-600 text-sm">
              No history yet — waiting for data
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickLine={false}
                  axisLine={{ stroke: "#1e293b" }}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={36}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: "0.5rem",
                    color: "#f1f5f9",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => [`${v.toFixed(2)} ${cfg.unit}`, cfg.label]}
                />
                {/* Normal range reference lines */}
                {cfg.alarmHigh != null && (
                  <line
                    y1={cfg.alarmHigh} y2={cfg.alarmHigh}
                    stroke="#ef4444" strokeDasharray="4 2" strokeWidth={1}
                  />
                )}
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={cfg.colour}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                  connectNulls
                  name={cfg.label}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
});
