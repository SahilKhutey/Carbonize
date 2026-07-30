import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, TrendingDown, Clock, DollarSign } from 'lucide-react';

export function ProblemView() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-4xl mx-auto space-y-10">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full mb-4">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-xs text-red-300 font-semibold">The Industry Problem</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Carbon Capture Economics Are Broken
          </h1>
          <p className="text-lg text-slate-400">Current amine solvents (MEA) create massive energy and degradation bottlenecks.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <PainCard
            icon={<DollarSign className="w-6 h-6" />}
            title="Too Expensive"
            stat="$50 / ton"
            statLabel="Current MEA capture cost"
            description="Solvent steam consumption and chemical makeup represent 30-50% of plant operating costs."
          />
          <PainCard
            icon={<TrendingDown className="w-6 h-6" />}
            title="Fast Degradation"
            stat="15% / year"
            statLabel="MEA degradation rate"
            description="Oxidative degradation slashes capture efficiency by 10% annually, requiring constant solvent reclaims."
          />
          <PainCard
            icon={<Clock className="w-6 h-6" />}
            title="Slow Traditional R&D"
            stat="5 Years"
            statLabel="Discovery to pilot duration"
            description="Trial-and-error chemistry costs over $50M per candidate with a 90% failure rate."
          />
          <PainCard
            icon={<AlertCircle className="w-6 h-6" />}
            title="High Steam Reboiler Duty"
            stat="4.2 GJ / ton"
            statLabel="Regeneration heat energy"
            description="High heat of absorption requires massive steam draw from industrial power plants."
          />
        </div>

        <div className="text-center pt-6">
          <button
            onClick={() => navigate('/demo/approach')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            See Our AI Discovery Approach <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function PainCard({ icon, title, stat, statLabel, description }: any) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-3">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center justify-center text-red-400">
          {icon}
        </div>
        <h3 className="text-lg font-bold text-white">{title}</h3>
      </div>
      <div className="text-3xl font-bold text-white font-mono">{stat}</div>
      <div className="text-xs text-slate-400">{statLabel}</div>
      <p className="text-xs text-slate-300 leading-relaxed">{description}</p>
    </div>
  );
}
