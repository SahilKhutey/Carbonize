import React from "react";
import { ShieldCheck, AlertTriangle, Cpu, Layers, Download, CheckCircle2 } from "lucide-react";

export interface TrustScore {
  trust_level: string;
  provenance_status: string;
  comparator_status: string;
  ci_90_coverage_pct: number;
  recommended_safety_margin_pct: number;
  hardware_guidance_text: string;
}

export interface HardwareSpecData {
  project_name: string;
  target_flue_gas_flow_nm3_hr: number;
  target_co2_capture_pct: number;
  reactor_volume_m3: number;
  column_diameter_m: number;
  column_height_m: number;
  residence_time_s: number;
  liquid_to_gas_ratio_l_per_nm3: number;
  applied_safety_margin_pct: number;
  sized_reactor_volume_m3: number;
  chitosan_wt_pct: number;
  chitosan_consumption_kg_per_day: number;
  ca_lime_consumption_kg_per_day: number;
  ca_enzyme_dosage_mg_per_l: number;
  mesh_replacement_interval_days: number;
  trust_score: TrustScore;
  notes?: string[];
}

interface HardwareSpecSheetViewProps {
  spec: HardwareSpecData;
  onExport?: () => void;
}

export function HardwareSpecSheetView({ spec, onExport }: HardwareSpecSheetViewProps) {
  const isHighTrust = spec.trust_score.trust_level.includes("HIGH");
  const isLowTrust = spec.trust_score.trust_level.includes("LOW") || spec.trust_score.trust_level.includes("DISCREPANT");

  const badgeColor = isHighTrust
    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
    : isLowTrust
    ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
    : "bg-amber-500/10 text-amber-400 border-amber-500/30";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 max-w-4xl mx-auto space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl font-bold tracking-tight text-white">{spec.project_name}</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Formal Reactor Sizing & Consumable Schedule Deliverable for Pilot Engineering Handoff
          </p>
        </div>

        {onExport && (
          <button
            onClick={onExport}
            className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-4 py-2.5 rounded-lg transition shadow-lg shadow-emerald-900/30"
          >
            <Download className="w-4 h-4" />
            Export Spec Handoff
          </button>
        )}
      </div>

      {/* Unified Hardware Trust Badge */}
      <div className={`p-4 rounded-lg border ${badgeColor} flex items-start gap-3`}>
        {isHighTrust ? (
          <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
        ) : (
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
        )}
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <span className="font-bold text-sm uppercase tracking-wider">{spec.trust_score.trust_level}</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-950/50 border border-slate-800 font-mono">
              Margin: +{spec.applied_safety_margin_pct}%
            </span>
          </div>
          <p className="text-xs opacity-90">{spec.trust_score.hardware_guidance_text}</p>
          <div className="flex flex-wrap gap-4 text-[11px] pt-1 opacity-85 font-mono">
            <span>Provenance: {spec.trust_score.provenance_status}</span>
            <span>Comparator: {spec.trust_score.comparator_status}</span>
            <span>90% CI Coverage: {spec.trust_score.ci_90_coverage_pct.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Primary Sizing Metrics Grid */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          Reactor Column Geometry & Flow Specifications
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Flue Gas Flow</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.target_flue_gas_flow_nm3_hr.toLocaleString()} <span className="text-xs font-normal text-slate-400">Nm³/h</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Base Volume (Vr)</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.reactor_volume_m3} <span className="text-xs font-normal text-slate-400">m³</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 bg-emerald-950/20 border-emerald-800/40">
            <div className="text-[11px] text-emerald-400 font-medium">Sized Volume (+{spec.applied_safety_margin_pct}%)</div>
            <div className="text-base font-bold text-emerald-300 mt-1">{spec.sized_reactor_volume_m3} <span className="text-xs font-normal text-emerald-400">m³</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Column Diameter (D)</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.column_diameter_m} <span className="text-xs font-normal text-slate-400">m</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Column Height (H)</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.column_height_m} <span className="text-xs font-normal text-slate-400">m</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Residence Time (τ)</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.residence_time_s} <span className="text-xs font-normal text-slate-400">s</span></div>
          </div>


          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">L/G Ratio</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.liquid_to_gas_ratio_l_per_nm3} <span className="text-xs font-normal text-slate-400">L/Nm³</span></div>
          </div>

          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Target CO₂ Capture</div>
            <div className="text-base font-bold text-emerald-400 mt-1">{spec.target_co2_capture_pct}%</div>
          </div>
        </div>
      </div>

      {/* Consumables & Chemical Schedule */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Consumable Schedule & Chemical Demand (24h Operation)
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-slate-950/40 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Chitosan Consumption</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.chitosan_consumption_kg_per_day} <span className="text-xs font-normal text-slate-400">kg/day</span></div>
            <div className="text-[10px] text-slate-500 mt-1">{spec.chitosan_wt_pct}% wt formulation</div>
          </div>

          <div className="bg-slate-950/40 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Lime / Ca²⁺ Demand</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.ca_lime_consumption_kg_per_day} <span className="text-xs font-normal text-slate-400">kg/day</span></div>
          </div>


          <div className="bg-slate-950/40 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">CA Enzyme Dosage</div>
            <div className="text-base font-bold text-slate-100 mt-1">{spec.ca_enzyme_dosage_mg_per_l} <span className="text-xs font-normal text-slate-400">mg/L</span></div>
          </div>

          <div className="bg-slate-950/40 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Mesh Replacement</div>
            <div className="text-base font-bold text-slate-100 mt-1">Every {spec.mesh_replacement_interval_days} <span className="text-xs font-normal text-slate-400">days</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
