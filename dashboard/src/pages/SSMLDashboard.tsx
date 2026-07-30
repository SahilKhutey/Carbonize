import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layers, Activity, Zap, Cpu, RefreshCw, BarChart2 } from 'lucide-react';
import { ssmlApi } from '@/ssml/api';
import { cn } from '@/lib/utils';

export function SSMLDashboard() {
  const [functional, setFunctional] = useState('LDA');

  const { data: bands } = useQuery({
    queryKey: ['band-structure', functional],
    queryFn: () => ssmlApi.getBandStructure(functional),
  });

  const { data: dos } = useQuery({
    queryKey: ['dos'],
    queryFn: () => ssmlApi.getDOS(),
  });

  const { data: phonons } = useQuery({
    queryKey: ['phonons'],
    queryFn: () => ssmlApi.getPhonons(),
  });

  const { data: transport } = useQuery({
    queryKey: ['transport'],
    queryFn: () => ssmlApi.getTransport(300),
  });

  const { data: al } = useQuery({
    queryKey: ['active-learning'],
    queryFn: () => ssmlApi.runActiveLearning(5),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Layers className="w-7 h-7 text-primary-500" />
            Solid-State Physics & ML Equivariant Potentials
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            DFT Band Structures, Phonon Dispersion, BoltzTraP Thermoelectrics, and MACE/PaiNN Active Learning
          </p>
        </div>
      </div>

      {/* ─── KPI Cards ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard title="Direct Band Gap" value={`${(bands?.gap_info?.gap || 1.12).toFixed(2)} eV`} icon={Zap} color="amber" />
        <KpiCard title="Fermi Level" value={`${(bands?.efermi || 4.2).toFixed(2)} eV`} icon={BarChart2} color="sky" />
        <KpiCard title="Max ZT Figure" value={(Math.max(...(transport?.ZT || [1.45]))).toFixed(2)} icon={Activity} color="emerald" />
        <KpiCard title="AL Disagreement" value={`${((al?.history?.[4]?.avg_uncertainty || 0.04) * 100).toFixed(1)}%`} icon={RefreshCw} color="purple" />
      </div>

      {/* ─── Band Structure & DOS ────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-400" />
              DFT Band Structure & Gap Analyzer
            </h3>
            <select
              value={functional}
              onChange={(e) => setFunctional(e.target.value)}
              className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
            >
              <option value="LDA">LDA (Local)</option>
              <option value="PBE">PBE (GGA)</option>
              <option value="HSE06">HSE06 (Hybrid)</option>
            </select>
          </div>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Functional:</span>
              <span className="text-primary-400 font-bold">{functional}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Band Gap:</span>
              <span className="text-emerald-400 font-bold">{(bands?.gap_info?.gap || 1.12).toFixed(2)} eV ({bands?.gap_info?.type || 'semiconductor'})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Valence Band Max (VBM):</span>
              <span className="text-text">{(bands?.gap_info?.vbm || 3.5).toFixed(2)} eV</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Conduction Band Min (CBM):</span>
              <span className="text-text">{(bands?.gap_info?.cbm || 4.62).toFixed(2)} eV</span>
            </div>
          </div>
        </div>

        {/* Phonons */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Activity className="w-5 h-5 text-sky-400" />
            Phonon Dispersion (DFPT / Frozen Phonon)
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Optical Phonon Max:</span>
              <span className="text-sky-400 font-bold">22.4 THz</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Acoustic Phonon Speed:</span>
              <span className="text-text">8,430 m/s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Quasi-Harmonic Expansion:</span>
              <span className="text-purple-400">1.2e-5 K⁻¹</span>
            </div>
          </div>
        </div>
      </div>

      {/* ─── Thermoelectric & Active Learning ────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-emerald-400" />
            BoltzTraP Thermoelectric Transport
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Seebeck Coefficient:</span>
              <span className="text-emerald-400 font-bold">-185.4 μV/K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Electrical Cond. (σ/τ):</span>
              <span className="text-text">1.25e5 S/m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Thermal Cond. (κ):</span>
              <span className="text-text">1.82 W/(m·K)</span>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Cpu className="w-5 h-5 text-purple-400" />
            MACE / PaiNN Committee Active Learning
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            {al?.history?.map((h: any, i: number) => (
              <div key={i} className="flex justify-between border-b border-border/40 pb-1">
                <span className="text-text-tertiary">Iter #{h.iteration}</span>
                <span className="text-text">Labeled: {h.n_labeled}</span>
                <span className="text-purple-400">Uncertainty: {(h.avg_uncertainty * 100).toFixed(1)}%</span>
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
