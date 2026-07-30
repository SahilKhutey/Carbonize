import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { ArrowRight, DollarSign, TrendingUp, Zap } from 'lucide-react';
import demoApi from '@/api/demo';

const DEFAULT_INPUTS = {
  plant_capacity_mt_per_year: 1000000,
  co2_capture_rate: 0.9,
  electricity_price_usd_per_kwh: 0.07,
  steam_price_usd_per_gj: 8.0,
  solvent_price_usd_per_kg: 2.5,
  carbon_credit_price_usd_per_ton: 40.0,
  discount_rate: 0.08,
};

export function ROIView() {
  const navigate = useNavigate();
  const [inputs, setInputs] = useState(DEFAULT_INPUTS);

  const { mutate, data, isPending } = useMutation({
    mutationFn: demoApi.calculateROI,
  });

  React.useEffect(() => {
    mutate(inputs);
  }, []);

  const roi = data?.roi_analysis ?? null;

  const cashFlow = useMemo(() => {
    if (!roi) return [];
    const annual = roi.annual_benefits_usd - roi.annual_costs_usd;
    return Array.from({ length: 10 }, (_, i) => ({
      year: i + 1,
      cumulative: -roi.initial_investment_usd + annual * (i + 1),
      annual,
    }));
  }, [roi]);

  const maxAbs = cashFlow.length ? Math.max(...cashFlow.map((c) => Math.abs(c.cumulative))) : 1;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-4">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-emerald-300 font-semibold">Interactive ROI Calculator</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">Calculate Your Plant ROI</h1>
          <p className="text-slate-400">Adjust parameters for your facility and see the financial impact in real time.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {roi && (
            <>
              <SummaryCard icon={<DollarSign className="w-5 h-5" />} label="Annual OPEX Savings" value={`$${(roi.annual_benefits_usd / 1e6).toFixed(1)}M/yr`} color="emerald" />
              <SummaryCard icon={<Zap className="w-5 h-5" />} label="Payback Period" value={`${roi.payback_period_months.toFixed(1)} months`} color="cyan" />
              <SummaryCard icon={<TrendingUp className="w-5 h-5" />} label="10-Year NPV" value={`$${(roi.npv_10_year_usd / 1e6).toFixed(1)}M`} color="purple" />
            </>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Inputs */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white">Plant Parameters</h2>
            {[
              { key: 'plant_capacity_mt_per_year', label: 'Plant Capacity (t CO₂/yr)', min: 100000, max: 5000000, step: 100000 },
              { key: 'electricity_price_usd_per_kwh', label: 'Electricity Price ($/kWh)', min: 0.02, max: 0.2, step: 0.01 },
              { key: 'steam_price_usd_per_gj', label: 'Steam Price ($/GJ)', min: 3, max: 20, step: 0.5 },
              { key: 'carbon_credit_price_usd_per_ton', label: 'Carbon Credit Price ($/t)', min: 0, max: 150, step: 5 },
              { key: 'discount_rate', label: 'Discount Rate', min: 0.04, max: 0.15, step: 0.01 },
            ].map(({ key, label, min, max, step }) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300">{label}</span>
                  <span className="text-emerald-400 font-mono">{(inputs as any)[key]}</span>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={step}
                  value={(inputs as any)[key]}
                  onChange={(e) => {
                    const next = { ...inputs, [key]: parseFloat(e.target.value) };
                    setInputs(next);
                    mutate(next);
                  }}
                  className="w-full accent-emerald-500"
                />
              </div>
            ))}
          </div>

          {/* Cash Flow Chart */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white">10-Year Cumulative Cash Flow</h2>
            {isPending ? (
              <div className="flex items-center justify-center h-40 text-slate-400 text-xs">Calculating…</div>
            ) : (
              <div className="space-y-2">
                {cashFlow.map((c) => {
                  const pct = (Math.abs(c.cumulative) / maxAbs) * 100;
                  const isPositive = c.cumulative >= 0;
                  return (
                    <div key={c.year} className="flex items-center gap-2 text-xs">
                      <span className="w-8 text-slate-400 text-right">Y{c.year}</span>
                      <div className="flex-1 bg-slate-800 rounded h-5 relative overflow-hidden">
                        <div
                          className={`h-full ${isPositive ? 'bg-emerald-500/70' : 'bg-red-500/60'} rounded transition-all duration-300`}
                          style={{ width: `${pct}%` }}
                        />
                        <span className={`absolute inset-0 flex items-center px-2 font-mono text-[10px] ${isPositive ? 'text-emerald-300' : 'text-red-300'}`}>
                          {isPositive ? '+' : ''}{(c.cumulative / 1e6).toFixed(1)}M
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            {roi && (
              <div className="border-t border-slate-800 pt-3 space-y-1 text-xs">
                <div className="flex justify-between"><span className="text-slate-400">Initial Investment</span><span className="text-white font-mono">${(roi.initial_investment_usd / 1e6).toFixed(1)}M</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Annual Benefits</span><span className="text-emerald-400 font-mono">${(roi.annual_benefits_usd / 1e6).toFixed(1)}M</span></div>
                <div className="flex justify-between"><span className="text-slate-400">IRR</span><span className="text-white font-mono">{(roi.irr * 100).toFixed(1)}%</span></div>
              </div>
            )}
          </div>
        </div>

        <div className="text-center pt-4">
          <button
            onClick={() => navigate('/demo/platform')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            See Live Platform Operations <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ icon, label, value, color }: any) {
  const c: Record<string, string> = {
    emerald: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    cyan: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
  };
  return (
    <div className={`border rounded-2xl p-5 space-y-2 ${c[color]}`}>
      <div className="flex items-center gap-2">{icon}<span className="text-xs text-slate-300">{label}</span></div>
      <div className="text-3xl font-extrabold font-mono">{value}</div>
    </div>
  );
}
