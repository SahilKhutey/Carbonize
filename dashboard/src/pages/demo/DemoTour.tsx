import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, ArrowLeft, X, Sparkles, CheckCircle } from 'lucide-react';
import demoApi from '@/api/demo';

export function DemoTour() {
  const navigate = useNavigate();
  const { data: tourData } = useQuery({
    queryKey: ['tour-steps'],
    queryFn: demoApi.getTourSteps,
  });

  const [step, setStep] = useState(0);
  const steps = tourData?.steps || [
    { id: 1, title: 'The Problem', subtitle: 'CO2 capture is expensive', content: 'Today\'s amines (MEA) cost $50/ton CO2. Solvent is 30-50% of OPEX. Plants lose 5-15% efficiency annually.' },
    { id: 2, title: 'Our Approach', subtitle: 'AI-designed chemistry', content: 'We use AI to screen 12,000+ solvent candidates per day, ranking them by predicted performance.' },
    { id: 3, title: 'Top Candidate: SOLV-0237', subtitle: 'The breakthrough', content: 'Predicted 32% less energy, 18% higher capacity, 8x slower degradation than MEA. Lab validated.' },
    { id: 4, title: 'Plant Impact', subtitle: 'ROI at your scale', content: 'At a 1Mt/yr plant: $26M/yr OPEX savings, < 6 month payback, $234M NPV over 10 years.' },
    { id: 5, title: 'Beyond Chemistry', subtitle: 'Full-stack platform', content: 'Live monitoring + anomaly detection + chaos engineering + predictive maintenance.' },
    { id: 6, title: 'Proof', subtitle: 'Validated externally', content: '92% accuracy on 30+ published datasets. 3 pilot LOIs signed.' },
  ];

  const current = steps[step];

  const next = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      navigate('/demo/contact');
    }
  };

  const prev = () => {
    if (step > 0) setStep(step - 1);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* ─── Top Bar ────────────────────────────────────────────── */}
      <div className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/demo')}>
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg" />
            <span className="text-xl font-bold text-white">Carbonize</span>
          </div>
          <button
            onClick={() => navigate('/demo')}
            className="text-slate-400 hover:text-white flex items-center gap-2 text-xs transition"
          >
            <X className="w-4 h-4" /> Exit Tour
          </button>
        </div>
      </div>

      {/* ─── Progress Bar ───────────────────────────────────────── */}
      <div className="fixed top-16 left-0 right-0 z-40 bg-slate-900/50">
        <div className="h-1 bg-slate-800">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-300"
            style={{ width: `${((step + 1) / steps.length) * 100}%` }}
          />
        </div>
        <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-between text-xs">
          <span className="text-slate-400">Step {step + 1} of {steps.length}</span>
          <span className="text-slate-200 font-semibold">{current.title}</span>
        </div>
      </div>

      {/* ─── Main Content ───────────────────────────────────────── */}
      <div className="pt-32 pb-24 px-6 flex-1 max-w-4xl mx-auto w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-3">
            <Sparkles className="w-3 h-3 text-emerald-400" />
            <span className="text-xs text-emerald-300">Guided Pitch Step #{step + 1}</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">{current.title}</h1>
          <p className="text-lg text-slate-400">{current.subtitle}</p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 mb-8 space-y-4">
          <p className="text-base text-slate-200 leading-relaxed">{current.content}</p>
        </div>

        <StepEmbed step={step} />

        {/* Bottom controls */}
        <div className="flex items-center justify-between mt-10 border-t border-slate-800 pt-6">
          <button
            onClick={prev}
            disabled={step === 0}
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-30 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
          >
            <ArrowLeft className="w-4 h-4" /> Previous
          </button>

          <div className="flex gap-2">
            {steps.map((_: any, i: number) => (
              <div
                key={i}
                className={`h-2 rounded-full transition-all ${i === step ? 'w-8 bg-emerald-500' : 'w-2 bg-slate-700'}`}
              />
            ))}
          </div>

          <button
            onClick={next}
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
          >
            {step === steps.length - 1 ? 'Schedule Pilot' : 'Next Step'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function StepEmbed({ step }: { step: number }) {
  if (step === 0) {
    return (
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-lg font-bold text-white">The Broken Economics of Carbon Capture</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-800/50 p-4 rounded-xl text-center">
            <div className="text-2xl font-bold text-white">$50/t</div>
            <div className="text-xs text-slate-400 mt-1">Current MEA Capture Cost</div>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-xl text-center">
            <div className="text-2xl font-bold text-white">30-50%</div>
            <div className="text-xs text-slate-400 mt-1">Solvent Share of OPEX</div>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-xl text-center">
            <div className="text-2xl font-bold text-white">600+</div>
            <div className="text-xs text-slate-400 mt-1">Global Plants Needing Upgrade</div>
          </div>
        </div>
      </div>
    );
  }
  if (step === 2) {
    return (
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Energy Cut</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">32.0%</div>
        </div>
        <div className="bg-cyan-500/10 border border-cyan-500/30 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Capacity Increase</div>
          <div className="text-2xl font-bold text-cyan-400 font-mono">18.0%</div>
        </div>
        <div className="bg-purple-500/10 border border-purple-500/30 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Degradation Cut</div>
          <div className="text-2xl font-bold text-purple-400 font-mono">8x Slower</div>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Lab Trial Velocity</div>
          <div className="text-2xl font-bold text-amber-400 font-mono">2 Weeks</div>
        </div>
      </div>
    );
  }
  return null;
}
