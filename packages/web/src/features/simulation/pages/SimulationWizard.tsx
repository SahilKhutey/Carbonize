/**
 * packages/web/src/features/simulation/pages/SimulationWizard.tsx
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, ArrowLeft, Settings2, Play, CheckCircle2 } from "lucide-react";
import { usePlantProfile } from "../../../hooks/usePlantProfile";

export function SimulationWizard() {
  const [step, setStep] = useState(1);
  const [selectedPlant, setSelectedPlant] = useState("");
  const [duration, setDuration] = useState(24);
  const [samples, setSamples] = useState(100);
  const [uqEnabled, setUqEnabled] = useState(true);
  
  const { plants } = usePlantProfile();
  const navigate = useNavigate();

  const handleNext = () => setStep((s) => s + 1);
  const handleBack = () => setStep((s) => s - 1);

  const handleSubmit = async () => {
    // Mock simulation submission
    const fakeId = `sim-run-${Math.floor(Math.random() * 1000)}`;
    // Wait briefly to simulate API call
    await new Promise((r) => setTimeout(r, 600));
    navigate(`/simulations/${fakeId}`);
  };

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight">New Simulation</h1>
        <p className="text-slate-400 mt-1">Configure and launch a new digital twin simulation run.</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center mb-8">
        {[1, 2, 3].map((s) => (
          <React.Fragment key={s}>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm border-2 transition-colors ${
              step === s 
                ? "bg-emerald-600 border-emerald-600 text-white" 
                : step > s 
                  ? "bg-emerald-900/50 border-emerald-500 text-emerald-400"
                  : "bg-slate-900 border-slate-700 text-slate-500"
            }`}>
              {step > s ? <CheckCircle2 className="w-4 h-4" /> : s}
            </div>
            {s < 3 && (
              <div className={`flex-1 h-0.5 mx-2 transition-colors ${step > s ? "bg-emerald-500/50" : "bg-slate-800"}`} />
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden min-h-[400px] flex flex-col">
        <div className="p-6 flex-1">
          {/* STEP 1: Select Plant */}
          {step === 1 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
              <h2 className="text-lg font-semibold text-white mb-4">Select Target Plant</h2>
              {plants.length === 0 ? (
                <div className="p-4 bg-slate-800 rounded-lg text-slate-400 text-sm">
                  No plant profiles available. Please create one first.
                </div>
              ) : (
                <div className="grid gap-3">
                  {plants.map((plant) => (
                    <button
                      key={plant.id}
                      onClick={() => setSelectedPlant(plant.id)}
                      className={`flex flex-col text-left p-4 rounded-xl border transition-all ${
                        selectedPlant === plant.id
                          ? "bg-emerald-900/20 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                          : "bg-slate-950/50 border-slate-700 hover:border-slate-500"
                      }`}
                    >
                      <span className="font-semibold text-slate-200">{plant.name}</span>
                      <span className="text-xs text-slate-500 mt-1">{plant.location} • Configured for typical CO₂ capture</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STEP 2: Parameters */}
          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Settings2 className="w-5 h-5 text-emerald-400" />
                Simulation Parameters
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    Simulation Horizon (Hours)
                  </label>
                  <input 
                    type="range" min="1" max="168" step="1"
                    value={duration} onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full accent-emerald-500"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>1h</span>
                    <span className="text-emerald-400 font-bold">{duration}h</span>
                    <span>168h (7 days)</span>
                  </div>
                </div>

                <hr className="border-slate-800" />

                <div className="flex items-start justify-between p-4 bg-slate-950 rounded-lg border border-slate-800">
                  <div>
                    <h3 className="text-sm font-medium text-slate-200">Uncertainty Quantification (UQ)</h3>
                    <p className="text-xs text-slate-500 mt-1">
                      Run Monte Carlo iterations to generate confidence intervals and sensitivity indices.
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0">
                    <input 
                      type="checkbox" 
                      className="sr-only peer" 
                      checked={uqEnabled}
                      onChange={(e) => setUqEnabled(e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-slate-700 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                </div>

                {uqEnabled && (
                  <div className="pl-4 border-l-2 border-slate-800 ml-2 animate-in fade-in zoom-in-95 duration-200">
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Monte Carlo Samples
                    </label>
                    <select 
                      value={samples}
                      onChange={(e) => setSamples(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg py-2 pl-3 pr-8 text-sm text-white focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                    >
                      <option value="100">100 (Fast, ~2 mins)</option>
                      <option value="500">500 (Standard, ~10 mins)</option>
                      <option value="2000">2,000 (High Precision, ~45 mins)</option>
                    </select>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* STEP 3: Review */}
          {step === 3 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
              <h2 className="text-lg font-semibold text-white mb-4">Review & Submit</h2>
              
              <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Target Plant:</span>
                  <span className="text-sm font-semibold text-slate-200">{plants.find(p => p.id === selectedPlant)?.name || selectedPlant}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Horizon:</span>
                  <span className="text-sm font-semibold text-slate-200">{duration} Hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Analysis Type:</span>
                  <span className="text-sm font-semibold text-slate-200">
                    {uqEnabled ? `Stochastic (UQ, ${samples} samples)` : 'Deterministic (Single Run)'}
                  </span>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-emerald-900/20 border border-emerald-900/50">
                <p className="text-sm text-emerald-400 font-medium">Estimated compute time: {uqEnabled ? (samples > 500 ? '~45 mins' : '~10 mins') : '< 1 min'}</p>
                <p className="text-xs text-emerald-500/70 mt-1">This will consume cloud simulation credits.</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex justify-between">
          <button
            onClick={handleBack}
            disabled={step === 1}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          
          {step < 3 ? (
            <button
              onClick={handleNext}
              disabled={step === 1 && !selectedPlant}
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="inline-flex items-center gap-2 px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-bold rounded-lg shadow-lg shadow-emerald-900/20 transition-colors"
            >
              Launch Simulation <Play className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
