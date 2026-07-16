/**
 * packages/web/src/features/digital-twin/components/LiveKPIGrid.tsx
 *
 * Responsive grid of live KPI tiles driven by TwinState.
 * Each tile shows a value + unit, a status colour, and a trend arrow.
 */

import React, { memo, useMemo } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { TwinState } from "../types/twin";
import { fmt } from "../utils/formatters";
import { AccessibleKpiCard } from "../../../components/kpi/AccessibleKpiCard";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface KPIDef {
  id: string;
  label: string;
  value: string | number;
  unit: string;
  status: "good" | "warning" | "critical" | "neutral";
  trend?: "up" | "down" | "flat";
  sublabel?: string;
  target?: number;
}

interface LiveKPIGridProps {
  state: TwinState;
}

function captureStatus(pct: number | null | undefined): KPIStatus {
  const v = pct ?? 0;
  return v >= 80 ? "good" : v >= 60 ? "warning" : "critical";
}

export const LiveKPIGrid = memo(function LiveKPIGrid({ state }: LiveKPIGridProps) {
  const { current_actuals: a, performance: p } = state;

  const kpis: KPIDef[] = useMemo(() => [
    {
      id: "co2_capture",
      label: "CO₂ Capture",
      value: p.co2_capture_pct ?? 0,
      unit: "%",
      status: captureStatus(p.co2_capture_pct),
      trend: "flat",
      target: 85,
    },
    {
      id: "so2_capture",
      label: "SO₂ Capture",
      value: p.so2_capture_pct ?? 0,
      unit: "%",
      status: captureStatus(p.so2_capture_pct),
      target: 95,
    },
    {
      id: "reactor_temp",
      label: "Reactor Temp",
      value: a.reactor_temp_c ?? 0,
      unit: "°C",
      status: Math.abs((a.reactor_temp_c ?? 40) - 40) < 5 ? "good" : "warning",
      sublabel: `SP: 40.0 °C`,
      target: 40,
    },
    {
      id: "mesh_dp",
      label: "Mesh ΔP",
      value: a.mesh_dp_mmH2O ?? 0,
      unit: "mmH₂O",
      status: (a.mesh_dp_mmH2O ?? 0) < 200
        ? "good"
        : (a.mesh_dp_mmH2O ?? 0) < 240
        ? "warning"
        : "critical",
      target: 200,
    },
    {
      id: "co2_outlet",
      label: "CO₂ Outlet",
      value: a.co2_outlet_pct ?? 0,
      unit: "%",
      status: (a.co2_outlet_pct ?? 0) < 3 ? "good" : "warning",
      target: 3,
    },
    {
      id: "so2_outlet",
      label: "SO₂ Outlet",
      value: a.so2_outlet_mg_nm3 ?? 0,
      unit: "mg/Nm³",
      status: (a.so2_outlet_mg_nm3 ?? 100) < 200 ? "good" : "critical",
      sublabel: "CPCB limit: 200",
      target: 200,
    },
  ], [a, p]);

  return (
    <div
      role="list"
      aria-label="Real-time performance metrics"
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 2xl:gap-6 gap-3 md:gap-4"
    >
      {kpis.map((kpi) => (
        <div key={kpi.id} role="listitem">
          <AccessibleKpiCard
            label={kpi.label}
            value={kpi.value}
            unit={kpi.unit}
            status={kpi.status}
            trend={kpi.trend}
            target={kpi.target}
            detailedDescription={kpi.sublabel}
          />
        </div>
      ))}
    </div>
  );
});
