import React, { useState, useEffect } from 'react';
import { 
  Beaker, 
  Settings2, 
  HelpCircle, 
  Zap, 
  RefreshCw, 
  ShieldCheck, 
  ArrowLeft,
  Flame,
  Leaf,
  Layers
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SimResults {
  success: boolean;
  message: string;
  efficiencies: {
    CO2: number;
    SO2: number;
    NOx: number;
    PM: number;
    Metal: number;
  };
  block_strength_mpa: number;
  block_grade: string;
  final_state: Record<string, number>;
}

export function ExperimentalLab() {
  const navigate = useNavigate();
  
  // Simulation Input States
  const [co2VolPct, setCo2VolPct] = useState(14.0);
  const [so2MgPerNm3, setSo2MgPerNm3] = useState(1200.0);
  const [noxInletPpm, setNoxInletPpm] = useState(250.0);
  const [caConcentrationMgL, setCaConcentrationMgL] = useState(12.0);
  const [calciumSourceGPerL, setCalciumSourceGPerL] = useState(35.0);
  const [crosslinkingDensity, setCrosslinkingDensity] = useState(0.5);
  const [mgSubstitutionRatio, setMgSubstitutionRatio] = useState(0.3);

  // Results State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [experimentalResults, setExperimentalResults] = useState<SimResults | null>(null);
  const [standardResults, setStandardResults] = useState<SimResults | null>(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Run Experimental Simulation
      const resExp = await fetch('/api/experimental/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          co2_vol_pct: co2VolPct,
          so2_mg_per_nm3: so2MgPerNm3,
          nox_inlet_ppm: noxInletPpm,
          ca_concentration_mg_l: caConcentrationMgL,
          calcium_source_g_per_l: calciumSourceGPerL,
          crosslinking_density: crosslinkingDensity,
          mg_substitution_ratio: mgSubstitutionRatio,
        }),
      });

      if (!resExp.ok) throw new Error('Experimental simulation failed');
      const dataExp = await resExp.json();
      setExperimentalResults(dataExp);

      // 2. Run Standard Baseline Simulation (No NOx, No Crosslinking, No Mg Substitution)
      const resStd = await fetch('/api/experimental/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          co2_vol_pct: co2VolPct,
          so2_mg_per_nm3: so2MgPerNm3,
          nox_inlet_ppm: 0.0,
          ca_concentration_mg_l: caConcentrationMgL,
          calcium_source_g_per_l: calciumSourceGPerL,
          crosslinking_density: 0.0,
          mg_substitution_ratio: 0.0,
        }),
      });

      if (!resStd.ok) throw new Error('Standard baseline simulation failed');
      const dataStd = await resStd.json();
      setStandardResults(dataStd);

    } catch (err: any) {
      setError(err.message || 'An error occurred during simulation');
    } finally {
      setLoading(false);
    }
  };

  // Run simulation on mount
  useEffect(() => {
    runSimulation();
  }, []);

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col">
      {/* Top Banner */}
      <header className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 flex items-center justify-between shrink-0 sticky top-0 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-emerald-400 font-extrabold text-xl tracking-tight">🧪 Material Science Lab</span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">Experimental</span>
            </div>
            <p className="text-xs text-slate-400">Optimize structural strength, bio-conversions, and multi-pollutant abatement strategies.</p>
          </div>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs px-4 py-2 rounded-lg transition-all shadow-lg disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Run Laboratory Grid
        </button>
      </header>

      {/* Main Grid */}
      <div className="flex-1 max-w-[1600px] w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden">
        
        {/* Left Side: Parameters Panel */}
        <section className="lg:col-span-1 bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5 space-y-6 flex flex-col h-full overflow-y-auto">
          <div className="flex items-center gap-2 text-white border-b border-slate-850 pb-3">
            <Settings2 className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider">Upgrade Parameters</h2>
          </div>

          {/* Crosslinking Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-400" /> Chitosan Crosslinking
              </span>
              <span className="text-indigo-400 font-mono font-bold">{(crosslinkingDensity * 100).toFixed(0)}%</span>
            </div>
            <input 
              type="range" 
              min="0.0" 
              max="1.0" 
              step="0.05"
              value={crosslinkingDensity}
              onChange={(e) => setCrosslinkingDensity(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[10px] text-slate-500 leading-normal">Stabilizes CA enzymes thermally by up to 50%, but slightly restricts amine binding sites.</p>
          </div>

          {/* Mg Substitution Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                <Leaf className="w-3.5 h-3.5 text-emerald-400" /> Mg²⁺ Substitution Ratio
              </span>
              <span className="text-emerald-400 font-mono font-bold">{(mgSubstitutionRatio * 100).toFixed(0)}%</span>
            </div>
            <input 
              type="range" 
              min="0.0" 
              max="1.0" 
              step="0.05"
              value={mgSubstitutionRatio}
              onChange={(e) => setMgSubstitutionRatio(parseFloat(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[10px] text-slate-500 leading-normal">Replaces calcium with magnesium to precipitate hydromagnesite binders, increasing block strength.</p>
          </div>

          {/* Flue Gas Inputs */}
          <div className="border-t border-slate-850 pt-4 space-y-4">
            <div className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Inlet Flue Gas Profile</div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 flex items-center gap-1">
                  <Flame className="w-3.5 h-3.5 text-amber-500" /> NOx Concentration
                </span>
                <span className="text-amber-500 font-mono font-bold">{noxInletPpm} ppm</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1000" 
                step="25"
                value={noxInletPpm}
                onChange={(e) => setNoxInletPpm(parseInt(e.target.value))}
                className="w-full accent-amber-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">CO₂ Vol %</label>
                <input 
                  type="number" 
                  value={co2VolPct}
                  onChange={(e) => setCo2VolPct(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs font-mono font-bold focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">SO₂ mg/Nm³</label>
                <input 
                  type="number" 
                  value={so2MgPerNm3}
                  onChange={(e) => setSo2MgPerNm3(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs font-mono font-bold focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Right Side: Experimental Results & Comparative Dash */}
        <main className="lg:col-span-3 space-y-6 flex flex-col h-full overflow-y-auto">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-4 text-xs font-medium">
              ⚠️ Error executing chemistry solver: {error}
            </div>
          )}

          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* CO2 Efficiency */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between">
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block">CO₂ Abatement</span>
                <span className="text-3xl font-black text-white tracking-tight mt-2 block">
                  {experimentalResults ? `${experimentalResults.efficiencies.CO2.toFixed(1)}%` : '--'}
                </span>
              </div>
              {experimentalResults && standardResults && (
                <span className={`text-[10px] font-bold mt-4 flex items-center gap-1 ${
                  experimentalResults.efficiencies.CO2 >= standardResults.efficiencies.CO2 ? 'text-emerald-400' : 'text-red-400'
                }`}>
                  {experimentalResults.efficiencies.CO2 >= standardResults.efficiencies.CO2 ? '▲' : '▼'}
                  {(experimentalResults.efficiencies.CO2 - standardResults.efficiencies.CO2).toFixed(1)}% vs. Baseline
                </span>
              )}
            </div>

            {/* NOx Efficiency */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between">
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block">NOx Conversion</span>
                <span className="text-3xl font-black text-white tracking-tight mt-2 block">
                  {experimentalResults ? `${experimentalResults.efficiencies.NOx.toFixed(1)}%` : '--'}
                </span>
              </div>
              <span className="text-[10px] text-amber-500 font-bold mt-4 flex items-center gap-1">
                ⚡ Fertilizer Grade Ca(NO₃)₂ Yield
              </span>
            </div>

            {/* Block Strength */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between">
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block">Structural Grade</span>
                <span className="text-3xl font-black text-indigo-400 tracking-tight mt-2 block">
                  {experimentalResults ? `${experimentalResults.block_strength_mpa.toFixed(1)} MPa` : '--'}
                </span>
              </div>
              <span className="text-[10px] text-slate-400 font-bold mt-4 flex items-center gap-1.5">
                🛡️ Grade: {experimentalResults?.block_grade}
              </span>
            </div>
          </div>

          {/* Detailed Species Table */}
          <div className="bg-slate-900/30 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <Beaker className="w-4 h-4 text-emerald-400" /> Reaction Phase Matrix
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-widest text-[9px] font-bold">
                    <th className="py-3 px-4">Material Target / Species</th>
                    <th className="py-3 px-4">Standard Baseline</th>
                    <th className="py-3 px-4 text-indigo-400">Experimental Matrix</th>
                    <th className="py-3 px-4 text-emerald-400">Relative Delta</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850 font-medium text-slate-300">
                  {/* CaCO3 */}
                  <tr>
                    <td className="py-4 px-4 font-semibold text-white">Precipitated Calcite (CaCO₃)</td>
                    <td className="py-4 px-4 font-mono">{standardResults?.final_state.CaCO3_s?.toFixed(2) ?? '--'} mol/m³</td>
                    <td className="py-4 px-4 font-mono text-indigo-400">{experimentalResults?.final_state.CaCO3_s?.toFixed(2) ?? '--'} mol/m³</td>
                    <td className="py-4 px-4 font-mono text-emerald-400">
                      {experimentalResults && standardResults ? (
                        `${((experimentalResults.final_state.CaCO3_s - standardResults.final_state.CaCO3_s) / (standardResults.final_state.CaCO3_s || 1) * 100).toFixed(1)}%`
                      ) : '--'}
                    </td>
                  </tr>

                  {/* MgCO3 */}
                  <tr>
                    <td className="py-4 px-4 font-semibold text-white">Precipitated Hydromagnesite (MgCO₃)</td>
                    <td className="py-4 px-4 font-mono">0.00 mol/m³</td>
                    <td className="py-4 px-4 font-mono text-indigo-400">{experimentalResults?.final_state.MgCO3_s?.toFixed(2) ?? '--'} mol/m³</td>
                    <td className="py-4 px-4 text-emerald-400">Upgrade Added</td>
                  </tr>

                  {/* Ca(NO3)2 */}
                  <tr>
                    <td className="py-4 px-4 font-semibold text-white">Calcium Nitrate Fertilizer Yield</td>
                    <td className="py-4 px-4 font-mono">0.00 mol/m³</td>
                    <td className="py-4 px-4 font-mono text-indigo-400">{experimentalResults?.final_state.CaNO3_s?.toFixed(2) ?? '--'} mol/m³</td>
                    <td className="py-4 px-4 text-amber-500">Agri-Resource Yielded</td>
                  </tr>

                  {/* Heavy Metal */}
                  <tr>
                    <td className="py-4 px-4 font-semibold text-white">Trace Heavy Metal Capture</td>
                    <td className="py-4 px-4 font-mono">{standardResults?.efficiencies.Metal.toFixed(1) ?? '--'}%</td>
                    <td className="py-4 px-4 font-mono text-indigo-400">{experimentalResults?.efficiencies.Metal.toFixed(1) ?? '--'}%</td>
                    <td className="py-4 px-4 font-mono text-red-400">
                      {experimentalResults && standardResults ? (
                        `${(experimentalResults.efficiencies.Metal - standardResults.efficiencies.Metal).toFixed(1)}%`
                      ) : '--'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
