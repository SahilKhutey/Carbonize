import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Brain, Zap, FlaskConical, BarChart3 } from 'lucide-react';
import demoApi from '@/api/demo';

export function ApproachView() {
  const navigate = useNavigate();
  const { data: comparison } = useQuery({
    queryKey: ['comparison'],
    queryFn: demoApi.getComparison,
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-4xl mx-auto space-y-10">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-4">
            <Brain className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-emerald-300 font-semibold">Our AI Methodology</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            AI-Designed Chemistry Validated in the Lab
          </h1>
          <p className="text-lg text-slate-400">Compressing 5 years of traditional R&D into 6 months of execution.</p>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          <Step number="1" icon={<Brain className="w-5 h-5" />} title="Screen" description="12,000+ candidates/day via MACE/PaiNN GNNs" metric="12,000 / day" />
          <Step number="2" icon={<FlaskConical className="w-5 h-5" />} title="Synthesize" description="Top 5 candidates synthesized in 3 weeks" metric="5 candidates" />
          <Step number="3" icon={<Zap className="w-5 h-5" />} title="Validate" description="VLE & kinetics validated in bench trials" metric="92.4% accuracy" />
          <Step number="4" icon={<BarChart3 className="w-5 h-5" />} title="Deploy" description="Digital twin pilot deployed in < 6 months" metric="< 6 months" />
        </div>

        {comparison && (
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 space-y-6">
            <h2 className="text-2xl font-bold text-white">Carbonize vs. Traditional Trial-and-Error</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <ComparisonCard isWinner={true} title="Carbonize AI Platform" data={comparison.carbonize} />
              <ComparisonCard isWinner={false} title="Traditional Trial-and-Error" data={comparison.traditional} />
            </div>
          </div>
        )}

        <div className="text-center pt-4">
          <button
            onClick={() => navigate('/demo/portfolio')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            Explore Solvent Portfolio <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function Step({ number, icon, title, description, metric }: any) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-2">
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 bg-emerald-500/20 border border-emerald-500/30 rounded-lg flex items-center justify-center text-emerald-400 font-bold text-xs">
          {number}
        </div>
        <div className="text-emerald-400">{icon}</div>
      </div>
      <h3 className="text-base font-bold text-white">{title}</h3>
      <p className="text-xs text-slate-400">{description}</p>
      <div className="text-xs font-mono text-emerald-400 pt-1">{metric}</div>
    </div>
  );
}

function ComparisonCard({ isWinner, title, data }: any) {
  return (
    <div className={`border rounded-xl p-5 space-y-3 ${isWinner ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-slate-800 bg-slate-900/40'}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-white text-base">{title}</h3>
        {isWinner && <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-semibold">10x FASTER</span>}
      </div>
      <div className="space-y-2 text-xs">
        <div className="flex justify-between"><span className="text-slate-400">Time to Discovery:</span><span className="font-mono text-white">{data.time_to_discovery_months} mo</span></div>
        <div className="flex justify-between"><span className="text-slate-400">Time to Pilot:</span><span className="font-mono text-white">{data.time_to_pilot_months} mo</span></div>
        <div className="flex justify-between"><span className="text-slate-400">Cost / Discovery:</span><span className="font-mono text-white">${(data.cost_per_discovery_usd / 1000).toFixed(0)}k</span></div>
        <div className="flex justify-between"><span className="text-slate-400">Evaluated Candidates:</span><span className="font-mono text-white">{data.candidates_evaluated.toLocaleString()}</span></div>
        <div className="flex justify-between"><span className="text-slate-400">Success Rate:</span><span className="font-mono text-emerald-400 font-bold">{(data.success_rate * 100).toFixed(0)}%</span></div>
      </div>
    </div>
  );
}
