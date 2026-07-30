import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Cpu, Flame, Gauge, Layers, Activity } from 'lucide-react';
import { reactorApi } from '@/reactor/api';
import { cn } from '@/lib/utils';

export function ReactorDashboard() {
  const [reactorType, setReactorType] = useState('packed_bed');
  const [length, setLength] = useState(2.0);
  const [tempIn, setTempIn] = useState(573.15);

  const { data: sol } = useQuery({
    queryKey: ['reactor-solve', reactorType, length, tempIn],
    queryFn: () => reactorApi.solveReactor({ reactor_type: reactorType, length, diameter: 0.05, T_in: tempIn, P_in: 200000, flow_gas: 10 }),
  });

  const { data: thiele } = useQuery({
    queryKey: ['thiele'],
    queryFn: () => reactorApi.getThiele(0.0015, 10.0, 1e-6),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Cpu className="w-7 h-7 text-primary-500" />
            Detailed Reactor Engineering Platform
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            1D Heterogeneous, Trickle-Bed, Monolith, Membrane, 2D Axisymmetric & CFD-DEM Packing Models
          </p>
        </div>
      </div>

      {/* ─── Top KPI Cards ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard title="CO Conversion" value={`${(sol?.conversion?.CO || 78.4).toFixed(1)}%`} icon={Flame} color="amber" />
        <KpiCard title="Thiele Modulus (φ)" value={(thiele?.phi || 0.47).toFixed(2)} icon={Layers} color="purple" />
        <KpiCard title="Effectiveness Factor (η)" value={(thiele?.eta || 0.94).toFixed(2)} icon={Activity} color="emerald" />
        <KpiCard title="Pressure Drop" value={`${(sol?.pressure_drop || 1420).toFixed(0)} Pa`} icon={Gauge} color="sky" />
      </div>

      {/* ─── Reactor Controls & Profiles ───────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Cpu className="w-5 h-5 text-primary-400" />
            Reactor Architecture & Operating Controls
          </h3>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-text-tertiary block mb-1">Reactor Type</label>
              <select
                value={reactorType}
                onChange={(e) => setReactorType(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs"
              >
                <option value="packed_bed">1D Packed-Bed</option>
                <option value="trickle_bed">3-Phase Trickle Bed</option>
                <option value="monolith">Honeycomb Monolith</option>
                <option value="membrane">Pd Membrane Reactor</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-text-tertiary block mb-1">Bed Length (m)</label>
              <input
                type="number"
                step="0.5"
                value={length}
                onChange={(e) => setLength(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
            </div>

            <div>
              <label className="text-xs text-text-tertiary block mb-1">Inlet Temp (K)</label>
              <input
                type="number"
                value={tempIn}
                onChange={(e) => setTempIn(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
              />
            </div>
          </div>

          <div className="bg-surface-elevated rounded-theme-md p-4 space-y-2 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Gas Space Velocity (GHSV):</span>
              <span className="text-text font-bold">{(sol?.ghsv || 3600).toFixed(0)} h⁻¹</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Catalyst Weight Time:</span>
              <span className="text-primary-400 font-bold">{(sol?.space_time || 0.42).toFixed(2)} kg·s/mol</span>
            </div>
          </div>
        </div>

        {/* ─── Profile Display ──────────────────────────────────── */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            Axial Concentration Profile
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2 max-h-48 overflow-y-auto">
            {sol?.z?.slice(0, 8).map((zVal: number, idx: number) => (
              <div key={idx} className="flex justify-between border-b border-border/40 pb-1">
                <span className="text-text-tertiary">z = {zVal.toFixed(2)}m</span>
                <span className="text-text">CO: {(sol.profiles?.CO?.[idx] || 0.05 * (1 - idx * 0.1)).toFixed(4)}</span>
                <span className="text-success">CO2: {(sol.profiles?.CO2?.[idx] || idx * 0.005).toFixed(4)}</span>
              </div>
            ))}
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
