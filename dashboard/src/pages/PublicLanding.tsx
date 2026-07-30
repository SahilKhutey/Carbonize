import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

export function PublicLanding() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* ─── Navigation ──────────────────────────────────────────────── */}
      <nav className="fixed top-0 w-full z-50 bg-slate-900/90 backdrop-blur border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg" />
            <span className="text-xl font-bold text-white tracking-tight">Carbonize</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#solution" className="text-slate-400 hover:text-white transition">Solution</a>
            <a href="#how-it-works" className="text-slate-400 hover:text-white transition">How it Works</a>
            <a href="#results" className="text-slate-400 hover:text-white transition">Validation</a>
            <Link to="/pricing" className="text-slate-400 hover:text-white transition">Pricing</Link>
            <Link to="/blog" className="text-slate-400 hover:text-white transition">Research Blog</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/demo" className="px-4 py-2 text-emerald-400 hover:text-emerald-300 font-medium text-sm">
              Live Pitch Demo
            </Link>
            <Link to="/demo/contact" className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-lg font-medium text-sm shadow-lg shadow-emerald-500/20">
              Schedule Pilot
            </Link>
          </div>
        </div>
      </nav>

      {/* ─── Hero ──────────────────────────────────────────────── */}
      <section className="pt-36 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-emerald-300 font-medium">92.4% Accuracy across 30+ Published Datasets</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight tracking-tight">
            Industrial Carbon Capture <br />
            <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent">
              at Half the Cost
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            AI-designed absorption solvents that outperform conventional MEA by <strong>32% lower energy</strong>, 
            <strong>18% higher capacity</strong>, and <strong>8x slower degradation</strong>.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              to="/demo/tour"
              className="group px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-2 shadow-xl shadow-emerald-500/25 transition"
            >
              Launch Interactive Tour
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </Link>
            <Link
              to="/demo/roi"
              className="px-8 py-4 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl font-bold text-lg transition"
            >
              Calculate Your Plant ROI
            </Link>
          </div>
          
          {/* ─── Key Stats ──────────────────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <StatCard value="31.9%" label="Energy Reduction" detail="2.45 vs 3.60 GJ/t CO₂" color="emerald" />
            <StatCard value="+18%" label="Cyclic Capacity" detail="0.69 vs 0.50 mol/mol" color="cyan" />
            <StatCard value="8x" label="Degradation Resistance" detail="2.0% vs 15.0%/year" color="violet" />
            <StatCard value="$21.6M" label="Annual OPEX Savings" detail="1 Mt/yr plant scale" color="amber" />
          </div>
        </div>
      </section>

      {/* ─── Problem vs Solution ────────────────────────────────── */}
      <section id="solution" className="py-20 px-6 bg-slate-900/50 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Chemistry is the Single Largest Bottleneck
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              $50/ton average capture cost. Solvent consumption drives 30–50% of plant OPEX.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6">
              <h3 className="text-xl font-bold text-red-400 flex items-center gap-2">
                <span>⚠️</span> Traditional Solvent R&D
              </h3>
              <div className="space-y-4 text-slate-300 text-sm">
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <strong className="text-white block mb-1">5 Years per Candidate</strong>
                  Trial-and-error synthesis in wet labs takes years per candidate with a 90% failure rate.
                </div>
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <strong className="text-white block mb-1">$5M+ R&D Expenditure</strong>
                  High cost per experimental campaign limits screening to ~50 molecules per decade.
                </div>
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <strong className="text-white block mb-1">15%/year Solvent Loss</strong>
                  Conventional monoethanolamine (MEA) degrades rapidly, creating toxic emissions and massive makeup costs.
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-950/60 to-cyan-950/60 border border-emerald-500/30 rounded-2xl p-8 space-y-6">
              <h3 className="text-xl font-bold text-emerald-400 flex items-center gap-2">
                <Sparkles className="w-5 h-5" /> Carbonize AI Platform
              </h3>
              <div className="space-y-4 text-slate-200 text-sm">
                <div className="flex items-start gap-3 p-4 bg-slate-900/80 rounded-xl border border-emerald-500/20">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white block mb-0.5">12,000+ Candidates / Day</strong>
                    Multi-objective Pareto optimization across loading, kinetics, heat of absorption, and thermal degradation.
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-slate-900/80 rounded-xl border border-emerald-500/20">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white block mb-0.5">6 Months to Pilot Skid</strong>
                    Compressing quantum DFT simulations, ML force fields, and lab validation into 180 days.
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-slate-900/80 rounded-xl border border-emerald-500/20">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white block mb-0.5">1.9 Month Payback</strong>
                    SOLV-0237 lead candidate delivers $21.6M annual net savings for a 1Mt/yr cement or steel capture plant.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Footer ──────────────────────────────────────────────── */}
      <footer className="py-10 px-6 bg-slate-950 border-t border-slate-800 text-center text-slate-500 text-sm">
        <p>© 2025 Carbonize, Inc. All rights reserved. AI-Designed Chemistry for Industrial Decarbonization.</p>
      </footer>
    </div>
  );
}

function StatCard({ value, label, detail, color }: any) {
  const colorClass: Record<string, string> = {
    emerald: 'text-emerald-400',
    cyan: 'text-cyan-400',
    violet: 'text-violet-400',
    amber: 'text-amber-400',
  };
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center">
      <div className={`text-3xl font-extrabold ${colorClass[color] || 'text-emerald-400'} mb-1`}>{value}</div>
      <div className="text-sm font-semibold text-slate-200">{label}</div>
      <div className="text-xs text-slate-500 mt-1">{detail}</div>
    </div>
  );
}
