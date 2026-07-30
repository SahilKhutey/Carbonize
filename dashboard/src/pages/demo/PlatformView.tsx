import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Activity, AlertTriangle, Shield, ArrowRight } from 'lucide-react';
import demoApi from '@/api/demo';

export function PlatformView() {
  const navigate = useNavigate();
  const { data: ops } = useQuery({
    queryKey: ['demo-operations'],
    queryFn: demoApi.getOperations,
  });
  const { data: chaosData } = useQuery({
    queryKey: ['demo-chaos'],
    queryFn: demoApi.getChaosResults,
  });

  const telemetry = ops?.telemetry?.slice(0, 24) ?? [];
  const chaos = chaosData?.chaos_results ?? [];

  const latest = telemetry[telemetry.length - 1] ?? null;

  const tabs = ['Live Telemetry', 'Anomaly Alerts', 'Chaos Drills'];
  const [tab, setTab] = useState(0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full mb-4">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span className="text-xs text-cyan-300 font-semibold">Live Operations Platform</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">Full-Stack Platform Intelligence</h1>
          <p className="text-slate-400">Real-time monitoring, ML anomaly detection, and automated chaos resilience testing.</p>
        </div>

        {/* KPI Strip */}
        {latest && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard label="CO₂ Removal Rate" value={`${(latest.co2_removal_efficiency * 100).toFixed(1)}%`} />
            <KpiCard label="Absorber Temp" value={`${latest.absorber_top_temperature_c.toFixed(1)} °C`} />
            <KpiCard label="Stripper Pressure" value={`${latest.stripper_pressure_bar.toFixed(2)} bar`} />
            <KpiCard label="Anomaly Score" value={latest.anomaly_score.toFixed(3)} highlight={latest.anomaly_score > 0.5} />
          </div>
        )}

        {/* Tab Bar */}
        <div className="flex border-b border-slate-800">
          {tabs.map((t, i) => (
            <button
              key={t}
              onClick={() => setTab(i)}
              className={`px-5 py-3 text-sm font-semibold transition border-b-2 -mb-[2px] ${
                tab === i ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === 0 && (
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4">24-Hour CO₂ Capture Efficiency</h2>
            <svg width="100%" height="120" viewBox={`0 0 ${telemetry.length * 20} 120`} preserveAspectRatio="none">
              {telemetry.map((d: any, i: number) => {
                const h = d.co2_removal_efficiency * 100;
                return (
                  <rect
                    key={i}
                    x={i * 20}
                    y={120 - h}
                    width={16}
                    height={h}
                    rx={2}
                    fill={d.anomaly_score > 0.5 ? '#ef4444' : '#10b981'}
                    opacity={0.7}
                  />
                );
              })}
            </svg>
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>24h ago</span><span>Now</span>
            </div>
          </div>
        )}

        {tab === 1 && (
          <div className="space-y-3">
            {telemetry.filter((d: any) => d.anomaly_score > 0.5).length === 0 ? (
              <div className="flex items-center gap-3 bg-slate-900/50 border border-emerald-700/30 rounded-xl p-4">
                <Shield className="w-5 h-5 text-emerald-400" />
                <span className="text-sm text-slate-200">No active anomalies — all systems nominal</span>
              </div>
            ) : (
              telemetry.filter((d: any) => d.anomaly_score > 0.5).map((d: any, i: number) => (
                <div key={i} className="flex items-center gap-3 bg-slate-900/50 border border-amber-700/30 rounded-xl p-4">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  <div className="text-sm">
                    <div className="text-white font-semibold">Anomaly detected — score {d.anomaly_score.toFixed(3)}</div>
                    <div className="text-slate-400 text-xs">{d.timestamp?.slice(0, 16).replace('T', ' ')} UTC</div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {tab === 2 && (
          <div className="space-y-3">
            {chaos.slice(0, 8).map((c: any, i: number) => (
              <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-white">{c.experiment_name ?? `Chaos Drill #${i + 1}`}</div>
                  <div className="text-xs text-slate-400">{c.status} — MTTR {c.mttr_minutes?.toFixed(0) ?? '—'} min</div>
                </div>
                <div className={`text-xs font-bold px-2 py-0.5 rounded ${c.steady_state_maintained ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                  {c.steady_state_maintained ? 'PASS' : 'FAIL'}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="text-center pt-4">
          <button
            onClick={() => navigate('/demo/validation')}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold text-base inline-flex items-center gap-2 transition"
          >
            See Model Validation Evidence <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`border rounded-xl p-4 space-y-1 ${highlight ? 'border-amber-500/40 bg-amber-500/5' : 'border-slate-800 bg-slate-900/50'}`}>
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-xl font-bold font-mono ${highlight ? 'text-amber-400' : 'text-white'}`}>{value}</div>
    </div>
  );
}
