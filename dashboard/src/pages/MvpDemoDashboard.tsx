import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Play, DollarSign, Award, Shield, FileText, CheckCircle2, ChevronRight, BarChart3, Rocket, Zap, Users } from 'lucide-react';
import { mvpApi } from '@/mvp/api';
import { cn } from '@/lib/utils';

export function MvpDemoDashboard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [plantCapacity, setPlantCapacity] = useState(1000000);
  const [steamCost, setSteamCost] = useState(15);
  const [activeTab, setActiveTab] = useState<'tour' | 'roi' | 'solvents' | 'architecture' | 'deck'>('tour');

  const { data: seed } = useQuery({
    queryKey: ['mvp-seed'],
    queryFn: () => mvpApi.getDemoSeed(),
  });

  const { data: roi } = useQuery({
    queryKey: ['mvp-roi', plantCapacity, steamCost],
    queryFn: () => mvpApi.calculateROI(plantCapacity, steamCost),
  });

  const { data: arch } = useQuery({
    queryKey: ['mvp-arch'],
    queryFn: () => mvpApi.getArchitecture('medium'),
  });

  const { data: pitch } = useQuery({
    queryKey: ['mvp-pitch'],
    queryFn: () => mvpApi.getPitchDeck(),
  });

  const steps = seed?.steps || [
    { step: 1, minute: '0-2', title: 'The Problem', subtitle: 'Solvent is 30-50% of OPEX. Amine degradation slashes 10%/yr efficiency.' },
    { step: 2, minute: '2-4', title: 'Our Approach', subtitle: 'Screen 10,000+ candidate absorbents/day using equivariant ML.' },
    { step: 3, minute: '4-6', title: 'SOLV-237 Lead', subtitle: '32% less energy, 18% higher capacity, 8x slower degradation.' },
    { step: 4, minute: '6-8', title: 'Plant Impact (ROI)', subtitle: '$8.0M/year OPEX savings at 1M t/yr plant (< 6-mo payback).' },
    { step: 5, minute: '8-9', title: 'Digital Twin Operations', subtitle: 'Real-time telemetry, failure forecast 3 days early, 92% chaos resilience.' },
    { step: 6, minute: '9-10', title: 'Proof & LOI', subtitle: 'Validated against 30+ published datasets with 92% accuracy. 3 active LOIs.' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* ─── Header ─────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-surface border border-border rounded-theme-md p-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-primary-500/10 text-primary-400 text-xs font-semibold px-2.5 py-1 rounded-full border border-primary-500/20">
              INVESTOR & CUSTOMER DEMO
            </span>
            <span className="text-text-tertiary text-xs">Carbonize AI Platform v2.0</span>
          </div>
          <h1 className="text-2xl font-bold text-text mt-2 flex items-center gap-2">
            <Rocket className="w-7 h-7 text-primary-500" />
            Strategic MVP & Investor Pitch Synthesis
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            End-to-End Guided Pitch Tour, Interactive ROI Business Case, SOLV-237 Validation, & Enterprise Architecture
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('tour')}
            className={cn('px-4 py-2 text-xs font-semibold rounded-theme-md transition-all', activeTab === 'tour' ? 'bg-primary-500 text-text' : 'bg-surface-elevated text-text-secondary hover:text-text')}
          >
            Guided 10-Min Pitch
          </button>
          <button
            onClick={() => setActiveTab('roi')}
            className={cn('px-4 py-2 text-xs font-semibold rounded-theme-md transition-all', activeTab === 'roi' ? 'bg-primary-500 text-text' : 'bg-surface-elevated text-text-secondary hover:text-text')}
          >
            ROI Calculator
          </button>
          <button
            onClick={() => setActiveTab('deck')}
            className={cn('px-4 py-2 text-xs font-semibold rounded-theme-md transition-all', activeTab === 'deck' ? 'bg-primary-500 text-text' : 'bg-surface-elevated text-text-secondary hover:text-text')}
          >
            Investor Deck
          </button>
        </div>
      </div>

      {/* ─── Main Content Tabs ─────────────────────────────────── */}
      {activeTab === 'tour' && (
        <div className="space-y-6">
          {/* Step Timeline */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            {steps.map((s: any) => (
              <button
                key={s.step}
                onClick={() => setCurrentStep(s.step)}
                className={cn(
                  'p-3 rounded-theme-md border text-left transition-all',
                  currentStep === s.step ? 'bg-primary-500/10 border-primary-500 text-text' : 'bg-surface border-border text-text-secondary hover:border-border/80'
                )}
              >
                <div className="text-[10px] uppercase font-bold text-primary-400">Min {s.minute}</div>
                <div className="text-xs font-semibold mt-1 truncate">{s.title}</div>
              </button>
            ))}
          </div>

          {/* Active Step Showcase Card */}
          <div className="bg-surface border border-border rounded-theme-md p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <span className="text-xs font-mono text-primary-400">STEP #{currentStep} OF 6</span>
                <h2 className="text-xl font-bold text-text mt-1">{steps[currentStep - 1]?.title}</h2>
                <p className="text-text-secondary text-sm">{steps[currentStep - 1]?.subtitle}</p>
              </div>
              <button
                onClick={() => setCurrentStep((prev) => (prev % 6) + 1)}
                className="flex items-center gap-2 bg-primary-500 text-text text-xs font-semibold px-4 py-2 rounded-theme-md hover:bg-primary-600 transition-all"
              >
                Next Step <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Dynamic Step Content */}
            {currentStep === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <HighlightCard title="Current Capture Cost" value="$40 - $80 / ton CO2" subtitle="30-50% OPEX tied to amine steam duty" icon={DollarSign} color="amber" />
                <HighlightCard title="Annual Efficiency Loss" value="5 - 15% / year" subtitle="Oxidative & thermal solvent degradation" icon={BarChart3} color="rose" />
                <HighlightCard title="Addressable Market" value="600+ Global Plants" subtitle="Cement, Steel, Power, and Refineries" icon={Users} color="sky" />
              </div>
            )}

            {currentStep === 3 && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
                <HighlightCard title="Energy Reduction" value="32.0% Less" subtitle="2.45 vs 3.60 GJ/ton CO2 reboiler duty" icon={Zap} color="emerald" />
                <HighlightCard title="Capacity Increase" value="18.0% Higher" subtitle="0.62 vs 0.50 mol CO2/mol amine" icon={BarChart3} color="sky" />
                <HighlightCard title="Degradation Rate" value="8x Slower" subtitle="0.18 vs 1.50 kg/ton solvent makeup" icon={Shield} color="purple" />
                <HighlightCard title="R&D Velocity" value="2 Weeks" subtitle="Synthesized vs 2 years traditional" icon={Award} color="amber" />
              </div>
            )}

            {currentStep === 4 && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
                <HighlightCard title="Annual OPEX Savings" value={`$${((roi?.annual_savings_usd || 8000000) / 1e6).toFixed(2)}M / year`} subtitle="At 1,000,000 t/yr CO2 plant scale" icon={DollarSign} color="emerald" />
                <HighlightCard title="10-Year Cumulative NPV" value={`$${((roi?.npv_10yr_usd || 64000000) / 1e6).toFixed(1)}M`} subtitle="Calculated at 8% WACC" icon={BarChart3} color="sky" />
                <HighlightCard title="Payback Period" value={`${(roi?.payback_months || 5.2).toFixed(1)} Months`} subtitle="Low retrofitting CAPEX requirement" icon={Rocket} color="purple" />
                <HighlightCard title="Reboiler Duty Savings" value="31.9% Steam Cut" subtitle="Directly lowers boiler fuel requirements" icon={Zap} color="amber" />
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'roi' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-surface border border-border rounded-theme-md p-5 space-y-4">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              Plant Parameters & Economics
            </h3>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-text-tertiary">Plant Capacity (t/yr CO2)</label>
                <input
                  type="number"
                  value={plantCapacity}
                  onChange={(e) => setPlantCapacity(Number(e.target.value))}
                  className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs mt-1"
                />
              </div>
              <div>
                <label className="text-xs text-text-tertiary">Steam Cost ($/GJ)</label>
                <input
                  type="number"
                  value={steamCost}
                  onChange={(e) => setSteamCost(Number(e.target.value))}
                  className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs mt-1"
                />
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 bg-surface border border-border rounded-theme-md p-5 space-y-4">
            <h3 className="font-semibold text-text text-base flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-sky-400" />
              Financial Savings & ROI Output
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-surface-elevated p-3 rounded-theme-md">
                <div className="text-[10px] text-text-tertiary">Annual OPEX Savings</div>
                <div className="text-lg font-bold text-emerald-400">${((roi?.annual_savings_usd || 8000000) / 1e6).toFixed(2)}M</div>
              </div>
              <div className="bg-surface-elevated p-3 rounded-theme-md">
                <div className="text-[10px] text-text-tertiary">10-Year NPV</div>
                <div className="text-lg font-bold text-sky-400">${((roi?.npv_10yr_usd || 64000000) / 1e6).toFixed(1)}M</div>
              </div>
              <div className="bg-surface-elevated p-3 rounded-theme-md">
                <div className="text-[10px] text-text-tertiary">Payback Period</div>
                <div className="text-lg font-bold text-purple-400">{(roi?.payback_months || 5.2).toFixed(1)} Mo</div>
              </div>
              <div className="bg-surface-elevated p-3 rounded-theme-md">
                <div className="text-[10px] text-text-tertiary">Retrofitting CAPEX</div>
                <div className="text-lg font-bold text-amber-400">${((roi?.retrofitting_capex_usd || 3500000) / 1e6).toFixed(2)}M</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'deck' && (
        <div className="bg-surface border border-border rounded-theme-md p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <h2 className="text-lg font-bold text-text flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary-400" />
                15-Slide Investor Pitch Deck & Pilot LOI Package
              </h2>
              <p className="text-text-secondary text-xs">Series A Pitch Narrative & Customer Commercialization Agreement</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-h-96 overflow-y-auto pr-2">
            {pitch?.slides?.map((slide: any) => (
              <div key={slide.slide} className="bg-surface-elevated border border-border/60 p-4 rounded-theme-md space-y-2">
                <div className="flex justify-between items-center text-xs font-bold text-primary-400">
                  <span>SLIDE #{slide.slide}</span>
                  <span>{slide.title}</span>
                </div>
                <p className="text-text text-xs leading-relaxed">{slide.headline}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function HighlightCard({ title, value, subtitle, icon: Icon, color }: any) {
  return (
    <div className="bg-surface-elevated border border-border/60 rounded-theme-md p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-text-tertiary">{title}</span>
        <Icon className={cn('w-5 h-5', color === 'amber' && 'text-amber-400', color === 'emerald' && 'text-emerald-400', color === 'rose' && 'text-rose-400', color === 'sky' && 'text-sky-400', color === 'purple' && 'text-purple-400')} />
      </div>
      <div className="text-2xl font-bold text-text font-mono">{value}</div>
      <p className="text-[11px] text-text-secondary">{subtitle}</p>
    </div>
  );
}
