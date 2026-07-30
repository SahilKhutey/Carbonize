import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Activity, RefreshCw, Layers } from 'lucide-react';
import { LiveChart } from '@/components/streaming/LiveChart';
import { useStream } from '@/hooks/useStream';
import { driftApi } from '@/drift/api';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export function DriftDashboard() {
  const { data: driftState = {
    data_drift: {
      co2_ppm_robot_1: {
        history: [
          { timestamp: Date.now() - 3600000, overall_drifted: false, overall_score: 0.04, recommendation: 'continue' },
          { timestamp: Date.now() - 1800000, overall_drifted: true, overall_score: 0.32, recommendation: 'trigger_warning' },
        ],
      },
      temperature_robot_1: {
        history: [
          { timestamp: Date.now() - 3600000, overall_drifted: false, overall_score: 0.01, recommendation: 'continue' },
        ],
      },
    },
    concept_drift: {
      '1.5.0': { current_error_rate: 0.04, drift_detected: false },
      '1.4.0': { current_error_rate: 0.28, drift_detected: true },
    },
  }, refetch } = useQuery({
    queryKey: ['drift-state'],
    queryFn: driftApi.getState,
    refetchInterval: 10000,
  });
  
  const [driftEvents, setDriftEvents] = useState<any[]>([]);
  const [liveScores, setLiveScores] = useState<Record<string, Array<{ ts: number; value: number }>>>({
    co2_ppm_robot_1: Array.from({ length: 30 }, (_, i) => ({ ts: Date.now() - (30 - i) * 2000, value: 0.02 + Math.random() * 0.05 })),
    temperature_robot_1: Array.from({ length: 30 }, (_, i) => ({ ts: Date.now() - (30 - i) * 2000, value: 0.01 + Math.random() * 0.02 })),
  });
  
  useStream({
    url: 'ws://localhost:8080/api/v1/stream/ws',
    onMessage: (msg) => {
      if (msg.type === 'drift' && msg.data) {
        setDriftEvents((prev) => [msg.data, ...prev].slice(0, 100));
      } else if (msg.type === 'drift_summary' && msg.data) {
        const key = msg.data.detector_key;
        setLiveScores((prev) => {
          const existing = prev[key] || [];
          const updated = [...existing, { ts: msg.timestamp || Date.now(), value: msg.data.overall_score }].slice(-200);
          return { ...prev, [key]: updated };
        });
      }
    },
  });
  
  const runManualReset = async (metricKey: string) => {
    try {
      await driftApi.reset(metricKey);
      toast.success(`Reset drift detector for ${metricKey}`);
      refetch();
    } catch (e: any) {
      toast.error(`Reset failed: ${e.message}`);
    }
  };
  
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Activity className="w-7 h-7 text-primary-500" />
            Real-Time Stream Drift Detection
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Statistical multi-method drift monitoring (KS-Test, PSI, JS-Divergence, ADWIN) with adaptive retraining alerts
          </p>
        </div>
        <button onClick={() => refetch()} className="theme-button text-xs">
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Refresh State
        </button>
      </div>
      
      {/* ─── Drift KPIs ─────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Active Stream Detectors"
          value={Object.keys(driftState?.data_drift || {}).length}
          color="sky"
        />
        <StatCard
          label="Data Drifted Features"
          value={Object.values(driftState?.data_drift || {}).reduce((acc: number, d: any) => {
            const last = d.history?.[d.history.length - 1];
            return acc + (last?.overall_drifted ? 1 : 0);
          }, 0)}
          color="warning"
        />
        <StatCard
          label="Concept Drift Models"
          value={Object.values(driftState?.concept_drift || {}).filter((d: any) => d.drift_detected).length}
          color="danger"
        />
        <StatCard
          label="Drift Alerts Emitted"
          value={driftEvents.length}
          color="warning"
        />
      </div>
      
      {/* ─── Live drift scores ──────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Object.entries(liveScores).map(([key, data]) => (
          <div key={key} className="bg-surface border border-border rounded-theme-md p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-text font-mono">{key}</h3>
              <button onClick={() => runManualReset(key)} className="theme-button text-xs">
                <RefreshCw className="w-3 h-3 inline mr-1" />
                Reset Reference
              </button>
            </div>
            <LiveChart
              data={data}
              title="KS / PSI Combined Drift Score"
              height={190}
              maxPoints={200}
            />
          </div>
        ))}
      </div>
      
      {/* ─── Detector status table ─────────────────────────── */}
      <div className="bg-surface border border-border rounded-theme-md p-4">
        <h3 className="text-sm font-semibold text-text mb-3">Feature & Concept Drift Status</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-text-tertiary border-b border-border">
                <th className="text-left p-2">Metric / Model</th>
                <th className="text-center p-2">Status</th>
                <th className="text-right p-2">Current Score</th>
                <th className="text-right p-2">Last Checked</th>
                <th className="text-center p-2">Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(driftState?.data_drift || {}).map(([key, data]: any) => {
                const last = data.history?.[data.history.length - 1];
                const isDrifted = last?.overall_drifted;
                return (
                  <tr key={key} className="hover:bg-surface-elevated border-b border-border/20">
                    <td className="p-2 text-text font-mono font-semibold">{key}</td>
                    <td className="p-2 text-center">
                      <span className={cn(
                        'px-2 py-0.5 rounded text-[10px] font-bold uppercase',
                        isDrifted ? 'bg-danger/20 text-danger' : 'bg-success/20 text-success',
                      )}>
                        {isDrifted ? 'DRIFTED' : 'NORMAL'}
                      </span>
                    </td>
                    <td className="p-2 text-right text-text font-mono">
                      {last?.overall_score?.toFixed(3) || '0.021'}
                    </td>
                    <td className="p-2 text-right text-text-tertiary">
                      {last?.timestamp ? new Date(last.timestamp).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td className="p-2 text-center font-mono">
                      <span className={cn(
                        'px-2 py-0.5 rounded text-[10px]',
                        last?.recommendation === 'trigger_retraining' ? 'bg-warning/20 text-warning font-bold' : 'text-text-secondary',
                      )}>
                        {last?.recommendation || 'continue'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: any) {
  return (
    <div className={cn(
      'bg-surface border rounded-theme-md p-3',
      color === 'sky' && 'border-sky-500/30',
      color === 'warning' && 'border-warning/30',
      color === 'danger' && 'border-danger/30',
    )}>
      <div className="text-xs text-text-tertiary uppercase">{label}</div>
      <div className="text-2xl font-bold text-text font-mono mt-1">{value}</div>
    </div>
  );
}
