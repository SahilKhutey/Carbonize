import React, { useState, useEffect } from "react";
import { 
  Flame, ShieldAlert, Activity, Cpu, Layers, RefreshCw, 
  AlertOctagon, CheckCircle2, ChevronRight, Droplets 
} from "lucide-react";

interface PollutantProp {
  id: string;
  name: string;
  formula: string;
  molar_mass_g_per_mol: number;
  henry_constant_mol_per_m3_pa: number;
  diffusivity_m2_per_s: number;
  cpcb_limit_mg_per_nm3: number;
  usepa_limit_mg_per_nm3: number;
  primary_system_impact: string;
  control_method: string;
}

interface ImpactAssessment {
  ph_drop_rate_per_min: number;
  ca_enzyme_inactivation_acceleration_factor: number;
  caso4_scaling_risk_index: number;
  chitosan_active_site_depletion_pct: number;
  recommended_lime_dosing_kg_per_hr: number;
  recommended_control_actions: string[];
}

export function PollutantsDatabasePage() {
  const [db, setDb] = useState<Record<string, PollutantProp>>({});
  const [assessment, setAssessment] = useState<ImpactAssessment | null>(null);
  const [loading, setLoading] = useState(true);

  // Input Sliders
  const [co2Vol, setCo2Vol] = useState(14.0);
  const [so2Ppm, setSo2Ppm] = useState(650.0);
  const [noxPpm, setNoxPpm] = useState(450.0);
  const [flyAshG, setFlyAshG] = useState(25.0);
  const [flowRate, setFlowRate] = useState(10000.0);

  const fetchDatabase = async () => {
    try {
      const res = await fetch("/api/pollutants/database");
      if (res.ok) {
        const data = await res.json();
        setDb(data);
      }
    } catch (err) {
      console.warn("Using fallback pollutants DB:", err);
    }
  };

  const assessImpact = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/pollutants/assess-impact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          co2_vol_pct: co2Vol,
          so2_mg_per_nm3: so2Ppm,
          nox_mg_per_nm3: noxPpm,
          fly_ash_g_per_nm3: flyAshG,
          exhaust_flow_nm3_hr: flowRate,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setAssessment(data);
      }
    } catch (err) {
      console.error("Impact assessment failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatabase();
    assessImpact();
  }, []);

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-8 text-slate-100 font-sans">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <Flame className="w-7 h-7 text-amber-500" />
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Chemistry & Pollutants Environmental Control Engine
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative thermodynamic properties, CPCB/USEPA limits, system degradation risk assessment, and bio-remediation control strategies.
          </p>
        </div>
        <button
          onClick={assessImpact}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
          Re-evaluate System Impact
        </button>
      </div>

      {/* Main Grid: Control Inputs & Live Impact Assessment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Flue Gas Composition Sliders */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
          <div className="flex items-center gap-2 text-white border-b border-slate-850 pb-3">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider">Flue Gas Feed Profile</h2>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between mb-1.5 font-medium">
                <span className="text-slate-300">CO₂ Concentration</span>
                <span className="text-emerald-400 font-mono font-bold">{co2Vol.toFixed(1)} Vol %</span>
              </div>
              <input
                type="range"
                min="2.0"
                max="30.0"
                step="0.5"
                value={co2Vol}
                onChange={(e) => setCo2Vol(parseFloat(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1.5 font-medium">
                <span className="text-slate-300">SO₂ Inlet Level</span>
                <span className="text-rose-400 font-mono font-bold">{so2Ppm.toFixed(0)} mg/Nm³</span>
              </div>
              <input
                type="range"
                min="0"
                max="2000"
                step="50"
                value={so2Ppm}
                onChange={(e) => setSo2Ppm(parseFloat(e.target.value))}
                className="w-full accent-rose-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-[10px] text-slate-500 mt-1">CPCB Norm: 200 mg/Nm³. High SO₂ causes Gypsum wall scaling.</p>
            </div>

            <div>
              <div className="flex justify-between mb-1.5 font-medium">
                <span className="text-slate-300">NOₓ (NO₂ equiv)</span>
                <span className="text-amber-400 font-mono font-bold">{noxPpm.toFixed(0)} mg/Nm³</span>
              </div>
              <input
                type="range"
                min="0"
                max="1500"
                step="25"
                value={noxPpm}
                onChange={(e) => setNoxPpm(parseFloat(e.target.value))}
                className="w-full accent-amber-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1.5 font-medium">
                <span className="text-slate-300">Fly Ash / PM Load</span>
                <span className="text-indigo-400 font-mono font-bold">{flyAshG.toFixed(1)} g/Nm³</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="2"
                value={flyAshG}
                onChange={(e) => setFlyAshG(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1.5 font-medium">
                <span className="text-slate-300">Exhaust Gas Flow Rate</span>
                <span className="text-cyan-400 font-mono font-bold">{flowRate.toLocaleString()} Nm³/hr</span>
              </div>
              <input
                type="range"
                min="1000"
                max="50000"
                step="1000"
                value={flowRate}
                onChange={(e) => setFlowRate(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Quantitative Impact & Control Actions */}
        <div className="lg:col-span-2 space-y-6">
          {assessment && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">pH Drop Rate</span>
                  <div className="text-xl font-bold text-rose-400 font-mono">
                    {assessment.ph_drop_rate_per_min.toFixed(3)} <span className="text-xs font-normal">/min</span>
                  </div>
                  <span className="text-[10px] text-slate-500">Acidification Velocity</span>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">CA Inactivation Acc.</span>
                  <div className="text-xl font-bold text-amber-400 font-mono">
                    {assessment.ca_enzyme_inactivation_acceleration_factor.toFixed(2)}x
                  </div>
                  <span className="text-[10px] text-slate-500">Thermal/Acid Stress</span>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">Gypsum Scaling Risk</span>
                  <div className="text-xl font-bold text-indigo-400 font-mono">
                    {(assessment.caso4_scaling_risk_index * 100).toFixed(0)}%
                  </div>
                  <span className="text-[10px] text-slate-500">CaSO₄ Precipitation</span>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">Lime Dosing Rate</span>
                  <div className="text-xl font-bold text-emerald-400 font-mono">
                    {assessment.recommended_lime_dosing_kg_per_hr.toFixed(1)} <span className="text-xs font-normal">kg/hr</span>
                  </div>
                  <span className="text-[10px] text-slate-500">Ca(OH)₂ Buffer Feed</span>
                </div>
              </div>

              {/* Recommended Remediation Actions */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  Automated Control & Remediation Actions
                </h3>
                <div className="space-y-2">
                  {assessment.recommended_control_actions.map((act, idx) => (
                    <div key={idx} className="bg-slate-950/60 border border-slate-850 p-3 rounded-lg flex items-start gap-2.5 text-xs">
                      <ChevronRight className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span className="text-slate-200 leading-relaxed">{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Bottom Table: Master Chemical & Statutory Pollutant Database */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          Master Flue Gas Pollutants Chemical & Regulatory Registry
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Pollutant</th>
                <th className="py-3 px-4">Molar Mass</th>
                <th className="py-3 px-4">Henry's H(25°C)</th>
                <th className="py-3 px-4">CPCB Limit</th>
                <th className="py-3 px-4">USEPA Limit</th>
                <th className="py-3 px-4">Primary System Impact</th>
                <th className="py-3 px-4">Control Strategy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {Object.values(db).map((p) => (
                <tr key={p.id} className="hover:bg-slate-850/50 transition">
                  <td className="py-3.5 px-4 font-bold text-white font-mono">{p.name} ({p.formula})</td>
                  <td className="py-3.5 px-4 font-mono">{p.molar_mass_g_per_mol} g/mol</td>
                  <td className="py-3.5 px-4 font-mono">{p.henry_constant_mol_per_m3_pa.toExponential(2)} mol/m³·Pa</td>
                  <td className="py-3.5 px-4 font-mono text-amber-400">{p.cpcb_limit_mg_per_nm3} mg/Nm³</td>
                  <td className="py-3.5 px-4 font-mono text-cyan-400">{p.usepa_limit_mg_per_nm3} mg/Nm³</td>
                  <td className="py-3.5 px-4 text-slate-400 max-w-xs leading-normal">{p.primary_system_impact}</td>
                  <td className="py-3.5 px-4 text-emerald-400 font-medium max-w-xs leading-normal">{p.control_method}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
