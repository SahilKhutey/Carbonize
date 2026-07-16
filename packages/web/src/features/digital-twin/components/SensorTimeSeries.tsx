/**
 * packages/web/src/features/digital-twin/components/SensorTimeSeries.tsx
 *
 * Rolling time-series chart for sensor readings, powered by Recharts.
 *
 * useStateHistory — accumulates a capped sliding window of TwinState readings.
 */

import React, { memo, useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Brush,
} from "recharts";
import { TwinState, SensorHistoryPoint } from "../types/twin";
import { epochToTimeStr } from "../utils/formatters";

// ---------------------------------------------------------------------------
// Colour palette for sensor lines
// ---------------------------------------------------------------------------

const LINE_COLOURS: Record<string, string> = {
  co2_inlet_pct:      "#60a5fa", // blue-400
  co2_outlet_pct:     "#34d399", // emerald-400
  so2_inlet_mg_nm3:   "#fbbf24", // amber-400
  so2_outlet_mg_nm3:  "#fb923c", // orange-400
  mesh_dp_mmH2O:      "#a78bfa", // violet-400
  reactor_temp_c:     "#f87171", // red-400
  pH:                 "#4ade80", // green-400
  flow_nm3_hr:        "#38bdf8", // sky-400
};

const DEFAULT_LINE_COLOUR = "#94a3b8"; // slate-400

// ---------------------------------------------------------------------------
// useStateHistory hook
// ---------------------------------------------------------------------------

const MAX_HISTORY = 120;

export function useStateHistory(
  currentState: TwinState | null,
  maxPoints = MAX_HISTORY,
): SensorHistoryPoint[] {
  const [history, setHistory] = useState<SensorHistoryPoint[]>([]);

  useEffect(() => {
    if (!currentState) return;
    setHistory((prev) => {
      const next = [
        ...prev,
        { timestamp: Date.now(), readings: { ...currentState.current_actuals } },
      ];
      return next.length > maxPoints ? next.slice(next.length - maxPoints) : next;
    });
  }, [currentState, maxPoints]);

  return history;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface SensorTimeSeriesProps {
  history: SensorHistoryPoint[];
  /** Keys of ActualsData to plot */
  metrics: string[];
  height?: number;
  /** Max data points to show in the Brush window */
  maxPoints?: number;
  /** Chart title */
  title?: string;
}

export const SensorTimeSeries = memo(function SensorTimeSeries({
  history,
  metrics,
  height = 280,
  maxPoints = 60,
  title = "Sensor History",
}: SensorTimeSeriesProps) {
  const data = history.slice(-maxPoints).map((pt) => ({
    time: epochToTimeStr(pt.timestamp),
    ...pt.readings,
  }));

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
        {title}
      </h3>
      {data.length === 0 ? (
        <div
          className="flex items-center justify-center text-slate-600 text-sm"
          style={{ height }}
        >
          Waiting for data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="time"
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={40}
            />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "0.5rem",
                color: "#f1f5f9",
                fontSize: 12,
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, color: "#94a3b8" }}
            />
            {metrics.map((metric) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={LINE_COLOURS[metric] ?? DEFAULT_LINE_COLOUR}
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
                connectNulls
              />
            ))}
            {data.length > 20 && (
              <Brush
                dataKey="time"
                height={18}
                stroke="#334155"
                fill="#0f172a"
                travellerWidth={6}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
});
