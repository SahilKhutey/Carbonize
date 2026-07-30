import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FlaskConical, Atom, ShieldAlert, Cpu, Sparkles, Database, Dna } from 'lucide-react';
import { labApi } from '@/lab/api';
import { cn } from '@/lib/utils';

export function LabDashboard() {
  const [amineType, setAmineType] = useState('primary');
  const [doeType, setDoeType] = useState('full_factorial');

  const { data: solvents } = useQuery({
    queryKey: ['solvents', amineType],
    queryFn: () => labApi.designSolvent(amineType),
  });

  const { data: doe } = useQuery({
    queryKey: ['doe', doeType],
    queryFn: () => labApi.createDoE(doeType),
  });

  const { data: hazop } = useQuery({
    queryKey: ['hazop'],
    queryFn: () => labApi.runHAZOP(),
  });

  const { data: hypotheses } = useQuery({
    queryKey: ['hypotheses'],
    queryFn: () => labApi.generateHypotheses(),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <FlaskConical className="w-7 h-7 text-primary-500" />
            Chemistry Experimentation & Closed-Loop Discovery
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Molecular Screening (COSMO-RS), DoE Optimization, LIMS Provenance, HAZOP Safety & Autonomous Hypotheses
          </p>
        </div>
      </div>

      {/* ─── Top Feature Cards ───────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard title="Solvent Candidates" value={solvents?.candidates?.length || 5} icon={Atom} color="amber" />
        <KpiCard title="DoE Experimental Runs" value={doe?.n_runs || 8} icon={Cpu} color="sky" />
        <KpiCard title="HAZOP Safety Nodes" value={hazop?.nodes?.length || 3} icon={ShieldAlert} color="purple" />
        <KpiCard title="Active Hypotheses" value={hypotheses?.hypotheses?.length || 2} icon={Sparkles} color="emerald" />
      </div>

      {/* ─── Molecular & DoE Section ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <Dna className="w-5 h-5 text-primary-400" />
              COSMO-RS Molecular Solvent Designer
            </h3>
            <select
              value={amineType}
              onChange={(e) => setAmineType(e.target.value)}
              className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
            >
              <option value="primary">Primary Amine</option>
              <option value="secondary">Secondary Amine</option>
              <option value="tertiary">Tertiary Amine</option>
              <option value="sterically_hindered">Sterically Hindered</option>
            </select>
          </div>

          <div className="space-y-2">
            {solvents?.candidates?.map((c: any, i: number) => (
              <div key={i} className="bg-surface-elevated rounded-theme-md p-3 flex justify-between items-center text-xs font-mono">
                <div>
                  <div className="font-bold text-text">{c.name}</div>
                  <div className="text-text-tertiary">Max Loading: {c.CO2_loading_max} mol/mol</div>
                </div>
                <div className="text-right">
                  <div className="text-primary-400 font-bold">Score: {c.overall_score.toFixed(1)}/100</div>
                  <div className="text-amber-400">${c.cost.toFixed(2)}/kg</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ─── DoE Matrix ───────────────────────────────────────── */}
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <Cpu className="w-5 h-5 text-sky-400" />
              Design of Experiments (DoE) Matrix
            </h3>
            <select
              value={doeType}
              onChange={(e) => setDoeType(e.target.value)}
              className="bg-surface-elevated border border-border rounded-theme-md px-3 py-1.5 text-text text-xs"
            >
              <option value="full_factorial">Full Factorial (2ᵏ)</option>
              <option value="fractional">Fractional Factorial (2ᵏ⁻ᵖ)</option>
              <option value="CCD">Central Composite (CCD)</option>
              <option value="BoxBehnken">Box-Behnken</option>
              <option value="PlackettBurman">Plackett-Burman</option>
            </select>
          </div>

          <div className="bg-surface-elevated rounded-theme-md p-3 max-h-56 overflow-y-auto font-mono text-xs space-y-1">
            {doe?.design?.slice(0, 8).map((run: number[], idx: number) => (
              <div key={idx} className="flex justify-between border-b border-border/40 pb-1">
                <span className="text-text-tertiary">Run #{idx + 1}</span>
                <span className="text-text">T: {run[0]?.toFixed(1)}K</span>
                <span className="text-text">P: {(run[1] / 1000)?.toFixed(0)}kPa</span>
                <span className="text-primary-400">Conc: {run[2]?.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── Safety HAZOP & Hypotheses ───────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-purple-400" />
            HAZOP Process Risk Analysis
          </h3>
          <div className="space-y-2 font-mono text-xs">
            {hazop?.nodes?.map((n: any, idx: number) => (
              <div key={idx} className="bg-surface-elevated rounded-theme-md p-3 flex justify-between items-center">
                <div>
                  <div className="font-bold text-text uppercase">{n.parameter} → {n.deviation}</div>
                  <div className="text-text-tertiary text-[11px]">{n.causes?.[0]}</div>
                </div>
                <span className={cn(
                  'px-2 py-0.5 rounded text-[10px] font-bold uppercase',
                  n.risk === 'medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                )}>
                  {n.risk} Risk
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
          <h3 className="font-semibold text-text text-base flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            Autonomous Discovery Hypotheses
          </h3>
          <div className="space-y-2">
            {hypotheses?.hypotheses?.map((h: any, idx: number) => (
              <div key={idx} className="bg-surface-elevated rounded-theme-md p-3 space-y-1 text-xs">
                <div className="font-semibold text-text">{h.statement}</div>
                <div className="text-text-tertiary text-[11px]">{h.rationale}</div>
                <div className="text-emerald-400 font-mono text-[10px]">Confidence: {(h.confidence * 100).toFixed(0)}%</div>
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
