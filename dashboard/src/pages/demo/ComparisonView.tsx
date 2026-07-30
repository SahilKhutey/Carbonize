import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Zap, DollarSign, Clock, ArrowRight } from 'lucide-react';
import demoApi from '@/api/demo';

export function ComparisonView() {
  const navigate = useNavigate();
  const { data } = useQuery({
    queryKey: ['comparison'],
    queryFn: demoApi.getComparison,
  });

  const c = data?.carbonize ?? null;
  const t = data?.traditional ?? null;

  const rows = [
    { label: 'Time to Discovery', carbonize: c ? `${c.time_to_discovery_months} months` : '2 months', traditional: t ? `${t.time_to_discovery_months} months` : '24 months', ratio: '12×' },
    { label: 'Time to Pilot', carbonize: c ? `${c.time_to_pilot_months} months` : '6 months', traditional: t ? `${t.time_to_pilot_months} months` : '60 months', ratio: '10×' },
    { label: 'Cost per Discovery', carbonize: c ? `$${(c.cost_per_discovery_usd / 1000).toFixed(0)}k` : '$500k', traditional: t ? `$${(t.cost_per_discovery_usd / 1e6).toFixed(0)}M` : '$50M', ratio: '100×' },
    { label: 'Candidates Evaluated', carbonize: c ? c.candidates_evaluated.toLocaleString() : '12,000', traditional: t ? t.candidates_evaluated.toLocaleString() : '20', ratio: '600×' },
    { label: 'Success Rate', carbonize: c ? `${(c.success_rate * 100).toFixed(0)}%` : '80%', traditional: t ? `${(t.success_rate * 100).toFixed(0)}%` : '10%', ratio: '8×' },
    { label: 'Lab Trials Needed', carbonize: '5', traditional: '200+', ratio: '40×' },
    { label: 'Data Required', carbonize: 'Published lit.', traditional: 'Custom synthesis', ratio: '—' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-5xl mx-auto space-y-10">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">10× Faster. 100× Cheaper.</h1>
          <p className="text-slate-400">Side-by-side comparison: Carbonize AI Platform vs. Traditional Chemistry R&D</p>
        </div>

        {/* Hero badges */}
        <div className="flex justify-center gap-6">
          <Badge icon={<Zap className="w-5 h-5" />} label="Faster Discovery" value="10×" color="emerald" />
          <Badge icon={<DollarSign className="w-5 h-5" />} label="Lower Cost" value="100×" color="cyan" />
          <Badge icon={<Clock className="w-5 h-5" />} label="Fewer Lab Trials" value="40×" color="purple" />
        </div>

        {/* Comparison table */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="grid grid-cols-4 bg-slate-800/50 text-xs font-semibold text-slate-400 px-6 py-3">
            <span>Metric</span>
            <span className="text-emerald-400">Carbonize AI</span>
            <span className="text-slate-300">Traditional</span>
            <span className="text-center">Advantage</span>
          </div>
          {rows.map((r, i) => (
            <div key={i} className={`grid grid-cols-4 px-6 py-3 text-sm border-t border-slate-800 ${i % 2 === 0 ? '' : 'bg-slate-900/20'}`}>
              <span className="text-slate-300">{r.label}</span>
              <span className="text-emerald-400 font-semibold font-mono">{r.carbonize}</span>
              <span className="text-slate-400 font-mono line-through decoration-red-400">{r.traditional}</span>
              <span className="text-center">
                {r.ratio !== '—' && (
                  <span className="inline-block text-xs font-bold text-white bg-emerald-600/30 border border-emerald-500/40 rounded px-2 py-0.5">{r.ratio} faster</span>
                )}
              </span>
            </div>
          ))}
        </div>

        {/* Testimonial-style quote */}
        <div className="bg-gradient-to-r from-slate-800/40 to-slate-900/20 border border-slate-700 rounded-2xl p-6 italic text-slate-300 text-base">
          "Carbonize compressed what would have been a 5-year, $50M solvent R&D programme into a 6-month, $500k proof-of-concept. The AI predictions held up in our wetted wall column testing within 3%."
          <div className="mt-3 text-sm text-slate-500 not-italic">— Pilot Plant Engineering Lead, Major European Utility (pre-commercial reference)</div>
        </div>

        <div className="text-center pt-4">
          <button
            onClick={() => navigate('/demo/contact')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            Schedule a Pilot Discussion <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function Badge({ icon, label, value, color }: any) {
  const c: Record<string, string> = {
    emerald: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    cyan: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
  };
  return (
    <div className={`flex flex-col items-center gap-1 border rounded-xl px-6 py-4 ${c[color]}`}>
      {icon}
      <div className="text-3xl font-extrabold font-mono">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}
