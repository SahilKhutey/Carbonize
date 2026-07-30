import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Sparkles, CheckCircle } from 'lucide-react';
import demoApi from '@/api/demo';

const RADAR_DIMS = [
  { key: 'co2_loading', label: 'CO₂ Loading' },
  { key: 'energy', label: 'Low Energy' },
  { key: 'rate', label: 'Abs. Rate' },
  { key: 'stability', label: 'Stability' },
  { key: 'volatility', label: 'Low Volatility' },
];

export function Solv237Detail() {
  const navigate = useNavigate();

  // Fetch the hero solvent + comparison to MEA (id: SOLV-0001)
  const { data: solventsData } = useQuery({
    queryKey: ['solvents-hero'],
    queryFn: () => demoApi.getSolvents({ sort_by: 'overall_score', limit: 20 }),
  });
  const { data: cmpData } = useQuery({
    queryKey: ['comparison'],
    queryFn: demoApi.getComparison,
  });

  const hero = solventsData?.solvents?.find((s: any) => s.is_hero);
  const mea = solventsData?.solvents?.[0]; // fallback

  const radarData: Record<string, { solv: number; mea: number }> = {
    co2_loading: { solv: 92, mea: 72 },
    energy: { solv: 88, mea: 58 },
    rate: { solv: 84, mea: 65 },
    stability: { solv: 95, mea: 38 },
    volatility: { solv: 90, mea: 70 },
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Hero Header */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-4">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-emerald-300 font-semibold">Hero Lead Candidate</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-3 tracking-tight">
            SOLV-0237
          </h1>
          <p className="text-lg text-slate-400">
            Tertiary alkanolamine blend — AI-designed, lab validated, ready for pilot.
          </p>
        </div>

        {/* Key Performance Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="Energy Reduction" value="32.0%" delta="+32% vs MEA" color="emerald" />
          <MetricCard label="CO₂ Loading" value="0.71 mol/mol" delta="+18% vs MEA" color="cyan" />
          <MetricCard label="Degradation" value="8× Slower" delta="vs MEA baseline" color="purple" />
          <MetricCard label="Predicted Accuracy" value="92.4%" delta="on 30+ datasets" color="amber" />
        </div>

        {/* Radar + Details Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-lg font-bold text-white mb-4">Performance Radar vs MEA</h2>
            <RadarChart data={radarData} />
            <div className="flex items-center justify-center gap-4 mt-4 text-xs">
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-400 inline-block" />SOLV-0237</div>
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-slate-400 inline-block" />MEA (Baseline)</div>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white">Lab Validation Results</h2>
            <div className="space-y-2 text-sm">
              {[
                { test: 'Wetted Wall Column (WWC) — 40°C', result: '✓ PASS', detail: 'Rate matches GNNs within 3%' },
                { test: 'VLE Vapor-Liquid Equilibrium', result: '✓ PASS', detail: 'Isotherm correct at 40/80°C' },
                { test: 'Oxidative Degradation Screen', result: '✓ PASS', detail: '8.2× slower than MEA' },
                { test: 'Corrosion (316L Steel 60 days)', result: '✓ PASS', detail: '< 0.05 mm/yr corrosion rate' },
                { test: 'Thermal Degradation 135°C', result: '✓ PASS', detail: 'Stable over 500 hr run' },
                { test: 'Foam Tendency Screen', result: '✓ PASS', detail: 'Low foam without antifoam additive' },
              ].map((r) => (
                <div key={r.test} className="flex items-start gap-3 bg-slate-800/30 rounded-lg p-3">
                  <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 text-xs">
                    <div className="text-white font-medium">{r.test}</div>
                    <div className="text-slate-400">{r.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Plant Scale Impact */}
        <div className="bg-gradient-to-r from-emerald-900/30 to-cyan-900/20 border border-emerald-700/30 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Plant-Scale Financial Impact (1 Mt/yr)</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ImpactCard label="Annual OPEX Savings" value="$26M" note="vs MEA baseline" />
            <ImpactCard label="Payback Period" value="< 6 mo" note="full retrofit cost" />
            <ImpactCard label="10-Year NPV" value="$234M" note="@ 8% discount rate" />
            <ImpactCard label="Carbon Credits" value="$8M/yr" note="@ $40/t CO₂" />
          </div>
        </div>

        <div className="text-center pt-4">
          <button
            onClick={() => navigate('/demo/roi')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            Calculate ROI for Your Plant <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, delta, color }: any) {
  const colors: Record<string, string> = {
    emerald: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/30 text-emerald-400',
    cyan: 'from-cyan-500/10 to-cyan-600/5 border-cyan-500/30 text-cyan-400',
    purple: 'from-purple-500/10 to-purple-600/5 border-purple-500/30 text-purple-400',
    amber: 'from-amber-500/10 to-amber-600/5 border-amber-500/30 text-amber-400',
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-4 space-y-1`}>
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-2xl font-bold font-mono ${colors[color].split(' ').pop()}`}>{value}</div>
      <div className="text-[10px] text-slate-500">{delta}</div>
    </div>
  );
}

function ImpactCard({ label, value, note }: any) {
  return (
    <div className="text-center space-y-1">
      <div className="text-3xl font-extrabold text-emerald-400">{value}</div>
      <div className="text-xs text-white font-semibold">{label}</div>
      <div className="text-[10px] text-slate-400">{note}</div>
    </div>
  );
}

function RadarChart({ data }: { data: Record<string, { solv: number; mea: number }> }) {
  const cx = 120, cy = 120, r = 90;
  const dims = Object.keys(data);
  const n = dims.length;

  const getPoint = (angle: number, val: number) => {
    const a = (angle - 90) * (Math.PI / 180);
    return {
      x: cx + (r * val / 100) * Math.cos(a),
      y: cy + (r * val / 100) * Math.sin(a),
    };
  };

  const angles = dims.map((_, i) => (360 / n) * i);

  const solvPath = dims.map((d, i) => {
    const p = getPoint(angles[i], data[d].solv);
    return `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`;
  }).join(' ') + 'Z';

  const meaPath = dims.map((d, i) => {
    const p = getPoint(angles[i], data[d].mea);
    return `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`;
  }).join(' ') + 'Z';

  return (
    <svg width="240" height="240" className="mx-auto">
      {/* Grid rings */}
      {[20, 40, 60, 80, 100].map((pct) => (
        <polygon
          key={pct}
          points={dims.map((_, i) => {
            const p = getPoint(angles[i], pct);
            return `${p.x},${p.y}`;
          }).join(' ')}
          fill="none"
          stroke="#334155"
          strokeWidth="1"
        />
      ))}
      {/* Axes */}
      {dims.map((_, i) => {
        const tip = getPoint(angles[i], 100);
        return <line key={i} x1={cx} y1={cy} x2={tip.x} y2={tip.y} stroke="#334155" strokeWidth="1" />;
      })}
      {/* MEA */}
      <path d={meaPath} fill="#94a3b8" fillOpacity={0.15} stroke="#94a3b8" strokeWidth={1.5} />
      {/* SOLV-0237 */}
      <path d={solvPath} fill="#10b981" fillOpacity={0.25} stroke="#10b981" strokeWidth={2} />
      {/* Labels */}
      {dims.map((d, i) => {
        const lp = getPoint(angles[i], 115);
        return (
          <text key={d} x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle" fill="#94a3b8" fontSize="9" fontFamily="monospace">
            {RADAR_DIMS[i].label}
          </text>
        );
      })}
    </svg>
  );
}
