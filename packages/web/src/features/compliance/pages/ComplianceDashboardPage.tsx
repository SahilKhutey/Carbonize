/**
 * packages/web/src/features/compliance/pages/ComplianceDashboardPage.tsx
 *
 * Environmental Regulatory Compliance & Emissions Verification Interface.
 * Tracks CPCB SO2 Limit compliance (200 mg/Nm³), MOEFCC Carbon Sequestration,
 * and heavy-metal leachate safety limits.
 */

import React from "react";
import { ShieldCheck, AlertCircle, FileCheck, Download, Award, CheckCircle2 } from "lucide-react";

export function ComplianceDashboardPage() {
  const complianceRules = [
    {
      agency: "CPCB (Central Pollution Control Board)",
      standard: "Thermal Power Plant Emission Norms",
      limit: "SO₂ ≤ 200 mg/Nm³",
      current: "18.4 mg/Nm³",
      status: "COMPLIANT",
      margin: "90.8% below statutory threshold",
    },
    {
      agency: "MOEFCC (Ministry of Environment)",
      standard: "Industrial Carbon Capture & Sequestration Mandate",
      limit: "CO₂ Capture ≥ 75.0%",
      current: "85.2%",
      status: "COMPLIANT",
      margin: "+10.2% above target",
    },
    {
      agency: "USEPA Method 1311 (TCLP)",
      standard: "Toxicity Characteristic Leaching Procedure",
      limit: "Pb < 5.0 mg/L, Cd < 1.0 mg/L",
      current: "Pb: 0.12 mg/L, Cd: 0.04 mg/L",
      status: "COMPLIANT",
      margin: "Safely immobilized in building block matrix",
    },
    {
      agency: "IS 12269 (Bureau of Indian Standards)",
      standard: "Ordinary Portland Cement Substitution Grade",
      limit: "Compressive Strength ≥ 28.5 MPa",
      current: "34.2 MPa",
      status: "COMPLIANT",
      margin: "Passes structural building block load test",
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            Regulatory Compliance & Carbon Credit Verification
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time verification against CPCB, MOEFCC, USEPA, and BIS structural standards.
          </p>
        </div>

        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 border border-slate-700 hover:border-slate-600 text-white rounded-xl text-xs font-bold transition-all">
          <Download className="w-4 h-4 text-emerald-400" />
          Export Compliance Audit Package (PDF)
        </button>
      </div>

      {/* Compliance Hero Badge */}
      <div className="bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0">
            <Award className="w-8 h-8 text-emerald-400" />
          </div>
          <div>
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest block">
              Audit Status: Fully Certified
            </span>
            <h2 className="text-xl font-black text-white mt-0.5">
              100% Environmental & Structural Compliance Verified
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              All plant operational parameters are locked within non-violating statutory safety envelopes.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 shrink-0">
          <div className="text-right">
            <span className="text-xs text-slate-400 block font-medium">Net CO₂ Sequestered</span>
            <span className="text-2xl font-black text-white">142,850 <span className="text-sm font-normal text-slate-400">tCO₂/yr</span></span>
          </div>
        </div>
      </div>

      {/* Standards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {complianceRules.map((rule) => (
          <div
            key={rule.standard}
            className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">
                  {rule.agency}
                </span>
                <h3 className="text-sm font-bold text-white mt-0.5">{rule.standard}</h3>
              </div>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {rule.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-500 block text-[11px]">Statutory Limit:</span>
                <span className="font-semibold text-slate-200">{rule.limit}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Measured Telemetry:</span>
                <span className="font-mono font-bold text-emerald-400">{rule.current}</span>
              </div>
            </div>

            <p className="text-xs text-slate-400 flex items-center gap-1.5">
              <FileCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              {rule.margin}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
