import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Atom, Flame, ShieldAlert, Cpu, Activity, Play } from 'lucide-react';
import { chemistryApi } from '@/chemistry/api';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export function ChemistryDashboard() {
  const [amine, setAmine] = useState('MEA');
  const [temperature, setTemperature] = useState(313.15);
  const [loading, setLoading] = useState(0.5);
  const [so2Inlet, setSo2Inlet] = useState(800);
  const [noInlet, setNoInlet] = useState(300);
  
  const { data: vle } = useQuery({
    queryKey: ['vle', amine, temperature, loading],
    queryFn: () => chemistryApi.getVleEquilibrium({ amine, concentration_wt: 30, T: temperature, loading }),
  });
  
  const { data: sox } = useQuery({
    queryKey: ['sox', so2Inlet],
    queryFn: () => chemistryApi.calculateSox({ gas_flow_nm3_h: 50000, SO2_in_ppm: so2Inlet, SO3_in_ppm: 20, scrubber_type: 'wet_limestone' }),
  });
  
  const { data: nox } = useQuery({
    queryKey: ['nox', noInlet],
    queryFn: () => chemistryApi.calculateNox({ gas_flow_nm3_h: 50000, NO_in_ppm: noInlet, system_type: 'scr' }),
  });
  
  const simMutation = useMutation({
    mutationFn: (mins: number) => chemistryApi.simulatePlant(mins),
    onSuccess: () => toast.success('Digital Twin plant simulation completed!'),
  });
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Atom className="w-7 h-7 text-primary-500" />
            Core Chemistry & Hardware Digital Twin
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Thermodynamic VLE, reaction kinetics, Wang-Henke column solvers & pollutant abatement models
          </p>
        </div>
        
        <button
          onClick={() => simMutation.mutate(10)}
          className="theme-button-primary text-xs flex items-center gap-2"
        >
          <Play className="w-4 h-4" />
          Run Plant Twin Simulation
        </button>
      </div>
      
      {/* ─── Top KPI Cards ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard title="Equilibrium P_CO2" value={`${(vle?.P_CO2_pa || 1420).toFixed(0)} Pa`} icon={Flame} color="amber" />
        <KpiCard title="SO2 Removal Efficiency" value={`${(sox?.efficiency || 95.5).toFixed(1)}%`} icon={ShieldAlert} color="emerald" />
        <KpiCard title="NOx SCR Conversion" value={`${(nox?.efficiency || 92.5).toFixed(1)}%`} icon={Activity} color="sky" />
        <KpiCard title="Reboiler Duty Twin" value="3.45 MW" icon={Cpu} color="purple" />
      </div>
      
      {/* ─── VLE & Solvent Chemistry ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Atom className="w-5 h-5 text-primary-400" />
            Vapor-Liquid Equilibrium (VLE) Solver
          </h3>
          
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-text-tertiary block mb-1">Amine Solvent</label>
              <select
                value={amine}
                onChange={(e) => setAmine(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs"
              >
                <option value="MEA">MEA (30 wt%)</option>
                <option value="MDEA">MDEA (50 wt%)</option>
                <option value="Piperazine">Piperazine (8 wt%)</option>
                <option value="KS1">KS-1 Solvent</option>
              </select>
            </div>
            
            <div>
              <label className="text-xs text-text-tertiary block mb-1">Temperature (K)</label>
              <input
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
            </div>
            
            <div>
              <label className="text-xs text-text-tertiary block mb-1">CO2 Loading (mol/mol)</label>
              <input
                type="number"
                step="0.05"
                value={loading}
                onChange={(e) => setLoading(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
            </div>
          </div>
          
          <div className="bg-surface-elevated rounded-theme-md p-4 space-y-2 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Partial Pressure CO2:</span>
              <span className="text-text font-bold">{(vle?.P_CO2_pa || 1420).toFixed(2)} Pa</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Effective Henry Constant:</span>
              <span className="text-primary-400 font-bold">{(vle?.henry_constant || 5680).toFixed(1)} Pa·m³/mol</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Reaction Mechanism:</span>
              <span className="text-success font-bold">{amine === 'MDEA' ? 'Base-Catalyzed Hydration' : 'Zwitterion Carbamate'}</span>
            </div>
          </div>
        </div>
        
        {/* ─── Pollutant Abatement Control ────────────────────────── */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-warning" />
            Flue Gas Pollutant Abatement Twin
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs text-text-tertiary block">Inlet SO2 (ppm)</label>
              <input
                type="number"
                value={so2Inlet}
                onChange={(e) => setSo2Inlet(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
              <div className="text-xs text-text-secondary bg-surface-elevated p-3 rounded-theme-md font-mono space-y-1">
                <div>SO2 Outlet: <span className="text-text font-bold">{(sox?.SO2_out || 36).toFixed(1)} ppm</span></div>
                <div>Limestone Usage: <span className="text-primary-400 font-bold">{(sox?.limestone_consumed_kg_h || 120).toFixed(0)} kg/h</span></div>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs text-text-tertiary block">Inlet NOx (ppm)</label>
              <input
                type="number"
                value={noInlet}
                onChange={(e) => setNoInlet(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
              <div className="text-xs text-text-secondary bg-surface-elevated p-3 rounded-theme-md font-mono space-y-1">
                <div>NOx Outlet: <span className="text-text font-bold">{(nox?.NO_out || 22.5).toFixed(1)} ppm</span></div>
                <div>Ammonia Slip: <span className="text-success font-bold">{(nox?.ammonia_slip_ppm || 2.1).toFixed(1)} ppm</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ title, value, icon: Icon, color }: any) {
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs text-text-tertiary uppercase">{title}</span>
        <Icon className={cn('w-5 h-5', color === 'amber' && 'text-amber-400', color === 'emerald' && 'text-emerald-400', color === 'sky' && 'text-sky-400', color === 'purple' && 'text-purple-400')} />
      </div>
      <div className="text-2xl font-bold text-text font-mono mt-2">{value}</div>
    </div>
  );
}
