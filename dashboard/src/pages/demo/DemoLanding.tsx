import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain } from 'lucide-react';
import demoApi from '@/api/demo';

export function DemoLanding() {
  const navigate = useNavigate();
  const { data: overview } = useQuery({
    queryKey: ['demo-overview'],
    queryFn: demoApi.getOverview,
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* ─── Top Navigation ────────────────────────────────────────── */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/demo')}>
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg" />
            <span className="text-xl font-bold text-white">Carbonize</span>
          </div>
          <div className="hidden md:flex items-center gap-6 text-sm">
            <button onClick={() => navigate('/demo/problem')} className="text-slate-300 hover:text-white transition">Problem</button>
            <button onClick={() => navigate('/demo/approach')} className="text-slate-300 hover:text-white transition">Approach</button>
            <button onClick={() => navigate('/demo/portfolio')} className="text-slate-300 hover:text-white transition">Solvent Portfolio</button>
            <button onClick={() => navigate('/demo/roi')} className="text-slate-300 hover:text-white transition">ROI Calculator</button>
            <button onClick={() => navigate('/dashboard')} className="text-slate-300 hover:text-white transition">Operator Console</button>
          </div>
          <button
            onClick={() => navigate('/demo/tour')}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium text-xs transition"
          >
            Start Tour →
          </button>
        </div>
      </nav>

      {/* ─── Hero Section ──────────────────────────────────────────── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-emerald-300">Backed by $2M seed funding</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Carbon capture at{' '}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              half the cost
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-300 mb-12 max-w-3xl mx-auto">
            AI-designed absorbents that outperform MEA by 32% in energy, 18% in capacity, and 8x in degradation resistance.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button
              onClick={() => navigate('/demo/tour')}
              className="group px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base flex items-center justify-center gap-2 shadow-2xl shadow-emerald-500/30 transition"
            >
              <Sparkles className="w-5 h-5" />
              See Live Pitch Demo
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </button>
            <button
              onClick={() => navigate('/demo/roi')}
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-base transition"
            >
              Calculate Plant ROI
            </button>
          </div>

          {/* Hero Stats */}
          {overview && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              <HeroStat value={(overview.metrics?.solvents_screened || 12000).toLocaleString()} label="Solvent Candidates Screened" icon={<Brain className="w-5 h-5" />} />
              <HeroStat value={`${overview.metrics?.avg_prediction_accuracy || 92.4}%`} label="Prediction Accuracy" icon={<TrendingUp className="w-5 h-5" />} />
              <HeroStat value={`${Math.round(overview.metrics?.avg_resilience_score || 94)}%`} label="Avg Resilience Score" icon={<Shield className="w-5 h-5" />} />
              <HeroStat value={`$${((overview.metrics?.largest_pilot_savings_usd || 26000000) / 1000000).toFixed(0)}M`} label="Largest Annual Pilot Savings" icon={<Sparkles className="w-5 h-5" />} />
            </div>
          )}
        </div>
      </section>

      {/* ─── Hero Candidate Preview ──────────────────────────────── */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Our Breakthrough Candidate: SOLV-0237
            </h2>
            <p className="text-slate-400">The sterically hindered amine-ether discovered by our equivariant ML model</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <ImprovementCard metric="Energy Reduction" value="32%" baseline="vs MEA baseline" color="emerald" />
            <ImprovementCard metric="Capacity Improvement" value="18%" baseline="vs MEA baseline" color="cyan" />
            <ImprovementCard metric="Degradation Resistance" value="8x" baseline="vs MEA baseline" color="violet" />
          </div>

          <div className="text-center mt-8">
            <button
              onClick={() => navigate('/demo/solv-237')}
              className="text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-2"
            >
              Read SOLV-0237 case study <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function HeroStat({ value, label, icon }: { value: string; label: string; icon: React.ReactNode }) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center justify-center gap-2 text-emerald-400 mb-2">{icon}</div>
      <div className="text-2xl font-bold text-white mb-1 font-mono">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}

function ImprovementCard({ metric, value, baseline, color }: any) {
  const borderClass = color === 'emerald' ? 'border-emerald-500/30 bg-emerald-500/10' : color === 'cyan' ? 'border-cyan-500/30 bg-cyan-500/10' : 'border-purple-500/30 bg-purple-500/10';
  return (
    <div className={`border rounded-xl p-6 ${borderClass}`}>
      <div className="text-xs text-slate-400 uppercase tracking-wider mb-2">{metric}</div>
      <div className="text-4xl font-bold text-white mb-2 font-mono">{value}</div>
      <div className="text-xs text-slate-300">{baseline}</div>
    </div>
  );
}
