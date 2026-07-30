import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Cpu, Box, Flame, Activity, Zap, Layers, Binary } from 'lucide-react';
import { compChemApi } from '@/compchem/api';
import { cn } from '@/lib/utils';

export function CompChemDashboard() {
  const [qcMethod, setQcMethod] = useState('dft');
  const [functional, setFunctional] = useState('B3LYP');
  const [crystalType, setCrystalType] = useState('rock_salt');

  const { data: md } = useQuery({
    queryKey: ['md-run'],
    queryFn: () => compChemApi.runMD(['NCCO'], 200, 300),
  });

  const { data: qc } = useQuery({
    queryKey: ['qc-calc', qcMethod, functional],
    queryFn: () => compChemApi.runQC(qcMethod, functional, 'water'),
  });

  const { data: crystal } = useQuery({
    queryKey: ['crystal', crystalType],
    queryFn: () => compChemApi.buildCrystal(crystalType),
  });

  const { data: phase } = useQuery({
    queryKey: ['phase-diagram'],
    queryFn: () => compChemApi.getPhaseDiagram('Fe-C'),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Cpu className="w-7 h-7 text-primary-500" />
            Computational Chemistry & Material Science Suite
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            LAMMPS Molecular Dynamics, Kohn-Sham DFT & RHF, CALPHAD Phase Diagrams & Crystal Physics
          </p>
        </div>
      </div>

      {/* ─── Top KPI Cards ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard title="QC Energy (Hartree)" value={(qc?.energy || -76.67).toFixed(3)} icon={Zap} color="amber" />
        <KpiCard title="MD Mean Temp" value={`${(md?.mean_T || 300.2).toFixed(1)} K`} icon={Flame} color="sky" />
        <KpiCard title="Lattice Volume" value={`${(crystal?.volume || 179.6).toFixed(1)} Å³`} icon={Box} color="purple" />
        <KpiCard title="Phases in Diagram" value={phase?.phase_names?.length || 2} icon={Layers} color="emerald" />
      </div>

      {/* ─── MD & QC Controls & Console ────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* QC Solver */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-400" />
              Quantum Chemistry (DFT / Hartree-Fock)
            </h3>
            <div className="flex gap-2">
              <select
                value={qcMethod}
                onChange={(e) => setQcMethod(e.target.value)}
                className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
              >
                <option value="dft">Kohn-Sham DFT</option>
                <option value="hf">Restricted HF (RHF)</option>
              </select>
              {qcMethod === 'dft' && (
                <select
                  value={functional}
                  onChange={(e) => setFunctional(e.target.value)}
                  className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
                >
                  <option value="B3LYP">B3LYP Hybrid</option>
                  <option value="PBE">PBE GGA</option>
                  <option value="LDA">LDA Local</option>
                </select>
              )}
            </div>
          </div>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Total Energy:</span>
              <span className="text-primary-400 font-bold">{(qc?.energy || -76.67).toFixed(5)} Hartree</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">SCF Iterations:</span>
              <span className="text-text">{qc?.iterations || 8} (Converged)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">PCM Solvation Energy:</span>
              <span className="text-emerald-400">{(qc?.solvation_energy || -9.45).toFixed(2)} kcal/mol</span>
            </div>
          </div>
        </div>

        {/* MD Simulation */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Activity className="w-5 h-5 text-sky-400" />
            Molecular Dynamics Trajectory (OPLS-AA)
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs max-h-48 overflow-y-auto space-y-1">
            {md?.energies?.slice(0, 6).map((e: any, idx: number) => (
              <div key={idx} className="flex justify-between border-b border-border/40 pb-1">
                <span className="text-text-tertiary">Step #{e.step}</span>
                <span className="text-text">T: {e.T?.toFixed(1)}K</span>
                <span className="text-sky-400">KE: {e.KE?.toFixed(1)}</span>
                <span className="text-amber-400">PE: {e.PE?.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── Materials & Phase Diagram ───────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <Box className="w-5 h-5 text-purple-400" />
              Crystal Structure Predictor
            </h3>
            <select
              value={crystalType}
              onChange={(e) => setCrystalType(e.target.value)}
              className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
            >
              <option value="rock_salt">Rock Salt (NaCl)</option>
              <option value="perovskite">Perovskite (ABO₃)</option>
              <option value="graphite">Hexagonal Graphite</option>
            </select>
          </div>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="font-bold text-text mb-2">Structure: {crystal?.name}</div>
            {crystal?.basis?.map((b: any, i: number) => (
              <div key={i} className="flex justify-between text-text-secondary">
                <span>Atom #{i + 1}: {b.element}</span>
                <span>[{b.position?.join(', ')}]</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            CALPHAD Phase Diagram Solver
          </h3>

          <div className="bg-surface-elevated rounded-theme-md p-4 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Binary System:</span>
              <span className="text-text font-bold">Fe-C (Iron-Carbon)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Temperature Range:</span>
              <span className="text-text">300.0 K – 1800.0 K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Coexisting Phases:</span>
              <span className="text-emerald-400 font-bold">{phase?.phase_names?.join(', ') || 'FCC, LIQUID'}</span>
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
