/**
 * packages/web/src/features/operator/components/KPIStrip.tsx
 *
 * 6-tile horizontal KPI strip — the operator's primary at-a-glance view.
 * Each tile is clickable → opens sensor drill-down.
 *
 * Design goals:
 *  - All 6 tiles visible without horizontal scroll on 24" monitor
 *  - Touch-friendly: each tile ≥ 44 px tall
 *  - Colour = alarm state (green / amber / red)
 *  - Value updates at 1 Hz (React memo + referential equality keeps DOM quiet)
 */

import React, { memo, useMemo } from "react";
import type { TwinState } from "../../digital-twin/types/twin";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type TileStatus = "good" | "warning" | "critical";

interface KPITileDef {
  id: string;
  label: string;
  value: string;
  unit: string;
  status: TileStatus;
  detail?: string; // e.g., "threshold: 200"
}

// ---------------------------------------------------------------------------
// Status styles (DCS alarm semantics)
// ---------------------------------------------------------------------------

const TILE_STYLE: Record<TileStatus, string> = {
  good:     "border-emerald-500 bg-emerald-900/30 text-emerald-300",
  warning:  "border-amber-500   bg-amber-900/30   text-amber-300",
  critical: "border-red-500     bg-red-900/30     text-red-300",
};

const VALUE_STYLE: Record<TileStatus, string> = {
  good:     "text-emerald-200",
  warning:  "text-amber-200",
  critical: "text-red-200",
};

// ---------------------------------------------------------------------------
// Single tile
// ---------------------------------------------------------------------------

interface TileProps {
  tile: KPITileDef;
  onClick?: (id: string) => void;
}

const KPITile = memo(function KPITile({ tile, onClick }: TileProps) {
  return (
    <button
      id={`kpi-tile-${tile.id}`}
      onClick={() => onClick?.(tile.id)}
      aria-label={`${tile.label}: ${tile.value} ${tile.unit}, status ${tile.status}`}
      className={`
        flex-1 min-w-0 min-h-[56px]
        px-3 py-2 rounded-lg border-l-4
        border border-slate-700
        ${TILE_STYLE[tile.status]}
        transition-all hover:brightness-110
        cursor-pointer text-left
        focus:outline-none focus:ring-2 focus:ring-offset-1
        focus:ring-offset-slate-900
      `}
    >
      <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest truncate">
        {tile.label}
      </p>
      <p className={`text-xl font-black tabular-nums leading-tight ${VALUE_STYLE[tile.status]}`}>
        {tile.value}
        <span className="text-[11px] font-medium text-slate-500 ml-0.5">{tile.unit}</span>
      </p>
      {tile.detail && (
        <p className="text-[10px] text-slate-600 truncate">{tile.detail}</p>
      )}
    </button>
  );
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number | null | undefined, decimals: number): string {
  return n == null ? "—" : n.toFixed(decimals);
}

function meshStatus(dp: number | null | undefined): TileStatus {
  const v = dp ?? 0;
  return v < 200 ? "good" : v < 240 ? "warning" : "critical";
}

function captureStatus(pct: number | null | undefined): TileStatus {
  const v = pct ?? 0;
  return v >= 80 ? "good" : v >= 60 ? "warning" : "critical";
}

function so2Status(mg: number | null | undefined): TileStatus {
  const v = mg ?? 0;
  return v < 200 ? "good" : "critical";
}

// ---------------------------------------------------------------------------
// Strip
// ---------------------------------------------------------------------------

interface KPIStripProps {
  state: TwinState;
  onTileClick?: (metricId: string) => void;
}

export const KPIStrip = memo(function KPIStrip({ state, onTileClick }: KPIStripProps) {
  const { current_actuals: a, performance: p } = state;

  const tiles: KPITileDef[] = useMemo(() => [
    {
      id: "co2_capture",
      label: "CO₂ Capture",
      value: fmt(p.co2_capture_pct, 1),
      unit: "%",
      status: captureStatus(p.co2_capture_pct),
    },
    {
      id: "so2_capture",
      label: "SO₂ Capture",
      value: fmt(p.so2_capture_pct, 1),
      unit: "%",
      status: captureStatus(p.so2_capture_pct),
    },
    {
      id: "reactor_temp_c",
      label: "Reactor Temp",
      value: fmt(a.reactor_temp_c, 1),
      unit: "°C",
      status: Math.abs((a.reactor_temp_c ?? 40) - 40) < 5 ? "good" : "warning",
      detail: "SP: 40.0 °C",
    },
    {
      id: "mesh_dp_mmH2O",
      label: "Mesh ΔP",
      value: fmt(a.mesh_dp_mmH2O, 0),
      unit: "mmH₂O",
      status: meshStatus(a.mesh_dp_mmH2O),
      detail: "Limit: 240",
    },
    {
      id: "pH",
      label: "pH",
      value: fmt(a.pH, 2),
      unit: "",
      status:
        (a.pH ?? 8) >= 8 && (a.pH ?? 8) <= 9 ? "good" : "warning",
      detail: "Target: 8.0–9.0",
    },
    {
      id: "so2_outlet_mg_nm3",
      label: "SO₂ Outlet",
      value: fmt(a.so2_outlet_mg_nm3, 0),
      unit: "mg/Nm³",
      status: so2Status(a.so2_outlet_mg_nm3),
      detail: "CPCB limit: 200",
    },
  ], [a, p]);

  return (
    <div
      role="region"
      aria-label="Live KPI strip"
      className="flex gap-2 px-4 py-2 overflow-x-auto"
    >
      {tiles.map((tile) => (
        <KPITile key={tile.id} tile={tile} onClick={onTileClick} />
      ))}
    </div>
  );
});
