import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Grid3x3, List, Sparkles } from 'lucide-react';
import demoApi from '@/api/demo';

export function SolventPortfolio() {
  const navigate = useNavigate();
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('overall_score');

  const { data } = useQuery({
    queryKey: ['demo-solvents', sortBy],
    queryFn: () => demoApi.getSolvents({ sort_by: sortBy, limit: 100 }),
  });

  const solvents = data?.solvents || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">12,000 Solvent Candidates Portfolio</h1>
          <p className="text-slate-400">Equivariant ML predicted thermodynamic performance & degradation resistance</p>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button onClick={() => setView('grid')} className={`p-2 rounded ${view === 'grid' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'}`}><Grid3x3 className="w-5 h-5" /></button>
            <button onClick={() => setView('list')} className={`p-2 rounded ${view === 'list' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'}`}><List className="w-5 h-5" /></button>
          </div>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white text-xs">
            <option value="overall_score">Sort by Overall Score</option>
            <option value="co2_loading_max">Sort by CO2 Loading</option>
            <option value="heat_of_absorption_kj_mol">Sort by Heat of Absorption</option>
          </select>
        </div>

        <div className={`grid gap-4 ${view === 'grid' ? 'grid-cols-2 md:grid-cols-4 lg:grid-cols-6' : 'grid-cols-1'}`}>
          {solvents.map((s: any) => (
            <SolventCard key={s.id} solvent={s} layout={view} onClick={() => s.is_hero && navigate('/demo/solv-237')} />
          ))}
        </div>
      </div>
    </div>
  );
}

function SolventCard({ solvent, layout, onClick }: any) {
  const isHero = solvent.is_hero;
  if (layout === 'list') {
    return (
      <div onClick={onClick} className={`bg-slate-900/50 border rounded-xl p-4 flex items-center gap-4 cursor-pointer hover:border-emerald-500/50 transition ${isHero ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-800'}`}>
        <div className="text-center min-w-[80px]">
          <div className="text-xs font-mono text-slate-400">{solvent.id}</div>
          <div className={`text-xl font-bold ${isHero ? 'text-emerald-400' : 'text-white'}`}>{solvent.overall_score.toFixed(0)}</div>
        </div>
        <div className="flex-1 grid grid-cols-4 gap-4 text-xs">
          <div><div className="text-slate-500">Loading</div><div className="text-white font-mono">{solvent.co2_loading_max.toFixed(2)} mol/mol</div></div>
          <div><div className="text-slate-500">ΔH (kJ/mol)</div><div className="text-white font-mono">{solvent.heat_of_absorption_kj_mol.toFixed(0)}</div></div>
          <div><div className="text-slate-500">Rate (1/s)</div><div className="text-white font-mono">{solvent.absorption_rate_1_s.toFixed(0)}</div></div>
          <div><div className="text-slate-500">Degradation</div><div className="text-white font-mono">{(solvent.degradation_rate_per_year * 100).toFixed(1)}%/yr</div></div>
        </div>
        {isHero && <Sparkles className="w-5 h-5 text-emerald-400" />}
      </div>
    );
  }
  return (
    <div onClick={onClick} className={`bg-slate-900/50 border rounded-xl p-3 cursor-pointer hover:border-emerald-500/50 transition ${isHero ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-800'}`}>
      <div className="text-center space-y-1">
        <div className="text-[10px] font-mono text-slate-500">{solvent.id}</div>
        <div className={`text-2xl font-bold ${isHero ? 'text-emerald-400' : 'text-white'}`}>{solvent.overall_score.toFixed(0)}</div>
        <div className="text-[10px] text-slate-400 truncate">{solvent.functional_group}</div>
        {isHero && <div className="text-[10px] font-bold text-emerald-400 pt-1">HERO LEAD</div>}
      </div>
    </div>
  );
}
