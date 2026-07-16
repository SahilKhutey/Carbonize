/**
 * packages/web/src/features/operator/components/PlantSchematic.tsx
 *
 * Live SVG schematic of the CBMS plant with animated sensor tags.
 *
 * Architecture:
 *  - Pure SVG drawn in React (no external SVG file dependency)
 *  - Each sensor tag: label + live value + status colour
 *  - Click any tag → onTagClick(metricId) for drill-down
 *
 * Layout (schematic):
 *  INLET → PRE-SCRUBBER → REACTOR TOWER → OUTLET
 *               ↓
 *          [Pump A/B] [Ultrasonic]
 */

import React, { memo } from "react";
import type { TwinState } from "../../digital-twin/types/twin";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type TagStatus = "good" | "warning" | "critical" | "offline";

interface SensorTag {
  id: string;
  label: string;
  value: string;
  unit: string;
  status: TagStatus;
  x: number;
  y: number;
}

// ---------------------------------------------------------------------------
// Tag colours
// ---------------------------------------------------------------------------

const TAG_FILL: Record<TagStatus, string> = {
  good:     "#064e3b",  // emerald-900
  warning:  "#451a03",  // amber-950
  critical: "#450a0a",  // red-950
  offline:  "#1e293b",  // slate-800
};
const TAG_STROKE: Record<TagStatus, string> = {
  good:     "#10b981",  // emerald-500
  warning:  "#f59e0b",  // amber-400
  critical: "#ef4444",  // red-500
  offline:  "#475569",  // slate-600
};
const TAG_TEXT: Record<TagStatus, string> = {
  good:     "#6ee7b7",  // emerald-300
  warning:  "#fcd34d",  // amber-300
  critical: "#fca5a5",  // red-300
  offline:  "#94a3b8",  // slate-400
};

// ---------------------------------------------------------------------------
// SVG sensor tag component
// ---------------------------------------------------------------------------

interface TagProps {
  tag: SensorTag;
  onClick?: (id: string) => void;
}

function Tag({ tag, onClick }: TagProps) {
  const W = 88, H = 40;
  return (
    <g
      id={`tag-${tag.id}`}
      transform={`translate(${tag.x - W / 2}, ${tag.y - H / 2})`}
      style={{ cursor: "pointer" }}
      role="button"
      aria-label={`${tag.label}: ${tag.value} ${tag.unit}, status ${tag.status}`}
      onClick={() => onClick?.(tag.id)}
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick?.(tag.id)}
    >
      <rect
        x={0} y={0} width={W} height={H} rx={6}
        fill={TAG_FILL[tag.status]}
        stroke={TAG_STROKE[tag.status]}
        strokeWidth={1.5}
      />
      {/* Pulsing dot for critical */}
      {tag.status === "critical" && (
        <circle cx={W - 8} cy={8} r={4} fill={TAG_STROKE["critical"]}>
          <animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite" />
        </circle>
      )}
      <text
        x={8} y={14}
        fontSize={9} fontWeight="600"
        fill={TAG_TEXT[tag.status]}
        fontFamily="monospace"
      >
        {tag.label}
      </text>
      <text
        x={8} y={30}
        fontSize={13} fontWeight="900"
        fill="#f1f5f9"
        fontFamily="monospace"
      >
        {tag.value}
        <tspan fontSize={9} fill="#94a3b8"> {tag.unit}</tspan>
      </text>
    </g>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number | null | undefined, d: number) {
  return n == null ? "—" : n.toFixed(d);
}

function meshStatus(v: number | null | undefined): TagStatus {
  const n = v ?? 0;
  return n < 200 ? "good" : n < 240 ? "warning" : "critical";
}

function soStatus(v: number | null | undefined): TagStatus {
  return (v ?? 0) < 200 ? "good" : "critical";
}

// ---------------------------------------------------------------------------
// Schematic
// ---------------------------------------------------------------------------

interface PlantSchematicProps {
  state: TwinState;
  onTagClick?: (metricId: string) => void;
}

const PIPE_COLOUR = "#334155";   // slate-700
const EQUIP_FILL  = "#0f172a";   // slate-950
const EQUIP_STROKE = "#475569";  // slate-600
const LABEL_FILL  = "#64748b";   // slate-500

export const PlantSchematic = memo(function PlantSchematic({
  state,
  onTagClick,
}: PlantSchematicProps) {
  const a = state.current_actuals;
  const p = state.performance;

  const tags: SensorTag[] = [
    {
      id: "co2_inlet_pct",
      label: "CO₂ Inlet",
      value: fmt(a.co2_inlet_pct, 1),
      unit: "%",
      status: "good",
      x: 100, y: 190,
    },
    {
      id: "so2_inlet_mg_nm3",
      label: "SO₂ Inlet",
      value: fmt(a.so2_inlet_mg_nm3, 0),
      unit: "mg/Nm³",
      status: "good",
      x: 100, y: 240,
    },
    {
      id: "pH",
      label: "pH",
      value: fmt(a.pH, 2),
      unit: "",
      status: (a.pH ?? 8) >= 8 && (a.pH ?? 8) <= 9 ? "good" : "warning",
      x: 300, y: 300,
    },
    {
      id: "reactor_temp_c",
      label: "T Reactor",
      value: fmt(a.reactor_temp_c, 1),
      unit: "°C",
      status: Math.abs((a.reactor_temp_c ?? 40) - 40) < 5 ? "good" : "warning",
      x: 500, y: 190,
    },
    {
      id: "mesh_dp_mmH2O",
      label: "Mesh ΔP",
      value: fmt(a.mesh_dp_mmH2O, 0),
      unit: "mmH₂O",
      status: meshStatus(a.mesh_dp_mmH2O),
      x: 500, y: 240,
    },
    {
      id: "co2_outlet_pct",
      label: "CO₂ Out",
      value: fmt(a.co2_outlet_pct, 2),
      unit: "%",
      status: (a.co2_outlet_pct ?? 0) < 3 ? "good" : "warning",
      x: 700, y: 190,
    },
    {
      id: "so2_outlet_mg_nm3",
      label: "SO₂ Out",
      value: fmt(a.so2_outlet_mg_nm3, 0),
      unit: "mg/Nm³",
      status: soStatus(a.so2_outlet_mg_nm3),
      x: 700, y: 240,
    },
    {
      id: "co2_capture_pct",
      label: "CO₂ Capture",
      value: fmt(p.co2_capture_pct, 1),
      unit: "%",
      status: (p.co2_capture_pct ?? 0) >= 80 ? "good" : "warning",
      x: 400, y: 60,
    },
  ];

  return (
    <div
      role="region"
      aria-label="Plant schematic"
      className="
        bg-slate-900/50 border border-slate-700 rounded-xl
        overflow-hidden w-full
      "
    >
      <div className="px-4 pt-3 pb-0">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
          Plant Schematic — Live
        </h2>
      </div>
      <svg
        viewBox="0 0 800 380"
        className="w-full"
        style={{ maxHeight: 380 }}
        aria-hidden="true"
      >
        {/* ——— Pipes ——— */}
        {/* Main duct: inlet → pre-scrubber */}
        <line x1={130} y1={210} x2={225} y2={210} stroke={PIPE_COLOUR} strokeWidth={8} />
        {/* Pre-scrubber → reactor */}
        <line x1={355} y1={210} x2={440} y2={210} stroke={PIPE_COLOUR} strokeWidth={8} />
        {/* Reactor → outlet */}
        <line x1={560} y1={210} x2={660} y2={210} stroke={PIPE_COLOUR} strokeWidth={8} />

        {/* ——— Equipment boxes ——— */}
        {/* Inlet duct */}
        <rect x={30} y={180} width={100} height={60} rx={6}
          fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={80} y={215} textAnchor="middle" fontSize={11} fontWeight="700"
          fill={LABEL_FILL}>INLET</text>

        {/* Pre-scrubber */}
        <rect x={225} y={160} width={130} height={100} rx={8}
          fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={290} y={210} textAnchor="middle" fontSize={11} fontWeight="700"
          fill={LABEL_FILL}>PRE-SCRUBBER</text>
        {/* Drain line down */}
        <line x1={290} y1={260} x2={290} y2={310} stroke={PIPE_COLOUR} strokeWidth={4} />

        {/* Reactor Tower */}
        <rect x={440} y={155} width={120} height={110} rx={8}
          fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={500} y={205} textAnchor="middle" fontSize={11} fontWeight="700"
          fill={LABEL_FILL}>REACTOR</text>
        <text x={500} y={220} textAnchor="middle" fontSize={10}
          fill={LABEL_FILL}>TOWER</text>

        {/* Outlet stack */}
        <rect x={660} y={180} width={110} height={60} rx={6}
          fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={715} y={215} textAnchor="middle" fontSize={11} fontWeight="700"
          fill={LABEL_FILL}>OUTLET</text>

        {/* Pump A */}
        <circle cx={250} cy={330} r={22} fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={250} y={334} textAnchor="middle" fontSize={9} fontWeight="700" fill={LABEL_FILL}>PUMP A</text>

        {/* Pump B */}
        <circle cx={310} cy={330} r={22} fill={EQUIP_FILL} stroke={EQUIP_STROKE} strokeWidth={1.5} />
        <text x={310} y={334} textAnchor="middle" fontSize={9} fontWeight="700" fill={LABEL_FILL}>PUMP B</text>

        {/* Sensor tags */}
        {tags.map((tag) => (
          <Tag key={tag.id} tag={tag} onClick={onTagClick} />
        ))}
      </svg>
    </div>
  );
});
