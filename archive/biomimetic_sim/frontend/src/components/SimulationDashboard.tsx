import React, { useState } from 'react';
import { usePollingSimulation } from '../hooks/usePollingSimulation.ts';
import { ComplianceBadge } from './ComplianceBadge.tsx';
import { FinancialChart } from './FinancialChart.tsx';

interface SimulationDashboardProps {
  plantId: string;
}

export const SimulationDashboard: React.FC<SimulationDashboardProps> = ({ plantId }) => {
  const [inputs, setInputs] = useState({
    press_force_bar: 200,
    enzyme_concentration_mg_l: 12.0,
    chitosan_wt_pct: 3.0,
    reactor_temperature_c: 40.0
  });

  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const { simulation, loading } = usePollingSimulation(activeRunId);

  const handleSliderChange = (name: string, value: number) => {
    setInputs(prev => ({ ...prev, [name]: value }));
  };

  const handleTriggerRun = async () => {
    try {
      const res = await fetch('/api/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plant_profile_id: plantId,
          ...inputs
        })
      });
      if (!res.ok) throw new Error('Failed to trigger simulation.');
      const data = await res.json();
      setActiveRunId(data.id);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 text-xs text-slate-100">
      
      {/* Left panel: Controls */}
      <aside className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col gap-6 shadow-lg">
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Operational Inputs
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">Control grid biological & compaction parameters.</p>
        </div>

        <div className="flex flex-col gap-4">
          {/* Enzyme */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between font-mono">
              <span className="text-slate-400">Enzyme Level (CA-KR1)</span>
              <span className="text-emerald-400 font-bold">{inputs.enzyme_concentration_mg_l} mg/L</span>
            </div>
            <input type="range" min="1" max="50" step="0.5" value={inputs.enzyme_concentration_mg_l} onChange={(e) => handleSliderChange('enzyme_concentration_mg_l', parseFloat(e.target.value))} className="w-full accent-emerald-500 bg-slate-950 h-1 rounded" />
          </div>

          {/* Chitosan */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between font-mono">
              <span className="text-slate-400">Chitosan Lattice Density</span>
              <span className="text-sky-400 font-bold">{inputs.chitosan_wt_pct} wt%</span>
            </div>
            <input type="range" min="1" max="5" step="0.1" value={inputs.chitosan_wt_pct} onChange={(e) => handleSliderChange('chitosan_wt_pct', parseFloat(e.target.value))} className="w-full accent-sky-500 bg-slate-950 h-1 rounded" />
          </div>

          {/* Press Force */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between font-mono">
              <span className="text-slate-400">Compaction Press Force</span>
              <span className="text-amber-400 font-bold">{inputs.press_force_bar} bar</span>
            </div>
            <input type="range" min="50" max="500" step="10" value={inputs.press_force_bar} onChange={(e) => handleSliderChange('press_force_bar', parseInt(e.target.value))} className="w-full accent-amber-500 bg-slate-950 h-1 rounded" />
          </div>

          {/* Temp */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between font-mono">
              <span className="text-slate-400">Reactor Temperature</span>
              <span className="text-rose-400 font-bold">{inputs.reactor_temperature_c} °C</span>
            </div>
            <input type="range" min="20" max="80" step="0.5" value={inputs.reactor_temperature_c} onChange={(e) => handleSliderChange('reactor_temperature_c', parseFloat(e.target.value))} className="w-full accent-rose-500 bg-slate-950 h-1 rounded" />
          </div>
        </div>

        <button onClick={handleTriggerRun} disabled={loading} className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2.5 rounded-lg transition-all disabled:opacity-50 mt-auto">
          {loading ? 'Solving Physical ODEs...' : 'Solve Process Run'}
        </button>
      </aside>

      {/* Middle & Right: Outputs */}
      <main className="lg:col-span-2 flex flex-col gap-6">
        {simulation?.result ? (
          <>
            {/* Top Stats Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <span className="text-slate-500 block text-[10px]">CO₂ Capture</span>
                <span className="text-lg font-bold text-emerald-400 mt-1 block">
                  {simulation.result.co2_capture_efficiency_pct.toFixed(1)} %
                </span>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <span className="text-slate-500 block text-[10px]">Block Compressive Strength</span>
                <span className="text-lg font-bold text-amber-400 mt-1 block">
                  {simulation.result.predicted_block_strength_mpa.toFixed(2)} MPa
                </span>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <span className="text-slate-500 block text-[10px]">Payback Period</span>
                <span className="text-lg font-bold text-sky-400 mt-1 block">
                  {simulation.result.simple_payback_months.toFixed(1)} Months
                </span>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                <span className="text-slate-500 block text-[10px]">Block Grade</span>
                <span className="text-[10px] font-bold text-slate-300 mt-1.5 block truncate">
                  {simulation.result.block_grade}
                </span>
              </div>
            </div>

            {/* Badges */}
            <ComplianceBadge
              cpcbCompliant={simulation.result.cpcb_compliant}
              value={simulation.result.so2_capture_efficiency_pct}
            />

            {/* Financial Chart */}
            <FinancialChart
              annualOpex={simulation.result.annual_opex_inr}
              annualBlockRevenue={simulation.result.annual_block_revenue_inr}
              annualCctsRevenue={simulation.result.annual_ccts_revenue_inr}
              capex={simulation.result.capex_total_inr}
            />

            {/* Report Download */}
            <a href={`/api/reports/${simulation.id}`} target="_blank" rel="noreferrer" className="w-fit bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-4 py-2 rounded-lg font-semibold transition-all">
              Download PDF Verification Report
            </a>
          </>
        ) : (
          <div className="flex-1 bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center p-12 text-slate-500 text-center gap-2">
            <span className="text-emerald-400 font-bold text-base">Ready for Processing</span>
            <p className="max-w-xs text-xs">Set inputs and hit "Solve Process Run" to compile physical kinetics models.</p>
          </div>
        )}
      </main>

    </div>
  );
};
