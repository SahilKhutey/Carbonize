import { useState } from 'react';
import { useStream } from '@/hooks/useStream';
import { AlertTriangle, Activity, Brain, GitBranch } from 'lucide-react';
import { cn } from '@/lib/utils';

export function AnomalyInvestigation() {
  const [anomalies, setAnomalies] = useState<any[]>([
    {
      timestamp: Date.now() - 60000,
      severity: 'critical',
      message: 'ML anomaly detected in co2_ppm (score=0.92)',
      context: {
        metric_type: 'co2_ppm',
        source_id: 'robot_1',
        value: 845.2,
        weighted_score: 0.92,
        scores: { autoencoder: 0.94, isolation_forest: 0.88, multimodal: 0.91 },
        correlated_anomalies: ['temperature_robot_1'],
      },
    },
    {
      timestamp: Date.now() - 300000,
      severity: 'high',
      message: 'ML anomaly detected in temperature (score=0.78)',
      context: {
        metric_type: 'temperature',
        source_id: 'robot_1',
        value: 38.5,
        weighted_score: 0.78,
        scores: { autoencoder: 0.76, isolation_forest: 0.81, multimodal: 0.75 },
        correlated_anomalies: [],
      },
    },
  ]);
  
  const [selectedAnomaly, setSelectedAnomaly] = useState<any | null>(anomalies[0]);
  
  useStream({
    url: 'ws://localhost:8080/api/v1/stream/ws',
    onMessage: (msg) => {
      if (msg.type === 'anomaly' && msg.data) {
        setAnomalies((prev) => [msg.data, ...prev].slice(0, 500));
      }
    },
  });
  
  const SEVERITY_COLORS = {
    critical: 'text-danger border-danger bg-danger/10',
    high: 'text-danger border-danger/50 bg-danger/5',
    medium: 'text-warning border-warning/50 bg-warning/5',
    low: 'text-text-secondary border-border bg-surface-hover',
  };
  
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Brain className="w-7 h-7 text-primary-500" />
            Anomaly Investigation
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            ML-based multi-modal anomaly detection with autoencoder + isolation forest
          </p>
        </div>
      </div>
      
      {/* ─── Stats ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard label="Active Anomalies" value={anomalies.filter((a) => Date.now() - a.timestamp < 300_000).length} icon={<AlertTriangle className="w-6 h-6" />} color="danger" />
        <StatCard label="Critical" value={anomalies.filter((a) => a.severity === 'critical').length} icon={<AlertTriangle className="w-6 h-6" />} color="danger" />
        <StatCard label="High" value={anomalies.filter((a) => a.severity === 'high').length} icon={<AlertTriangle className="w-6 h-6" />} color="warning" />
        <StatCard label="Total (1h)" value={anomalies.filter((a) => Date.now() - a.timestamp < 3600_000).length} icon={<Activity className="w-6 h-6" />} color="sky" />
      </div>
      
      <div className="grid grid-cols-12 gap-4">
        {/* ─── Anomaly list ──────────────────────────────────────── */}
        <div className="col-span-5 bg-surface border border-border rounded-theme-md p-4">
          <h3 className="text-sm font-semibold text-text mb-3">Recent Anomalies</h3>
          <div className="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto">
            {anomalies.length === 0 ? (
              <div className="text-center text-text-tertiary py-8">
                <Brain className="w-12 h-12 mx-auto opacity-30 mb-3" />
                No anomalies detected
              </div>
            ) : (
              anomalies.map((a, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedAnomaly(a)}
                  className={cn(
                    'w-full text-left p-3 rounded-theme-md border transition-colors',
                    SEVERITY_COLORS[a.severity as keyof typeof SEVERITY_COLORS],
                    selectedAnomaly?.timestamp === a.timestamp && 'ring-2 ring-primary-500',
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-sm font-medium">
                        {a.context?.metric_type || 'Unknown'}
                      </span>
                      <span className="text-xs uppercase opacity-70">{a.severity}</span>
                    </div>
                    <span className="text-xs opacity-70">
                      {new Date(a.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-xs mt-1 opacity-80">{a.message}</p>
                  {a.context?.correlated_anomalies?.length > 0 && (
                    <div className="flex items-center gap-1 mt-1">
                      <GitBranch className="w-3 h-3" />
                      <span className="text-xs opacity-70">
                        +{a.context.correlated_anomalies.length} correlated
                      </span>
                    </div>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
        
        {/* ─── Investigation panel ───────────────────────────────── */}
        <div className="col-span-7 bg-surface border border-border rounded-theme-md p-4">
          {selectedAnomaly ? (
            <AnomalyDetail anomaly={selectedAnomaly} />
          ) : (
            <div className="text-center text-text-tertiary py-12">
              <Brain className="w-12 h-12 mx-auto opacity-30 mb-3" />
              Click an anomaly to investigate
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AnomalyDetail({ anomaly }: { anomaly: any }) {
  const context = typeof anomaly.context === 'string' ? JSON.parse(anomaly.context) : anomaly.context;
  
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-text mb-1">Anomaly Details</h3>
        <p className="text-sm text-text-secondary">{anomaly.message}</p>
      </div>
      
      {/* ─── Detection scores ───────────────────────────────────── */}
      <div className="bg-surface-elevated rounded-theme-md p-3">
        <h4 className="text-xs font-semibold text-text-tertiary uppercase mb-3">Detection Scores</h4>
        <div className="space-y-2">
          {context?.scores && Object.entries(context.scores).map(([method, score]: any) => (
            <div key={method} className="flex items-center gap-2">
              <span className="w-32 text-xs text-text-secondary font-mono">{method}</span>
              <div className="flex-1 h-2 bg-surface rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full transition-all',
                    score > 0.7 ? 'bg-danger' : score > 0.5 ? 'bg-warning' : 'bg-success',
                  )}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
              <span className="text-xs font-mono text-text w-12 text-right">{(score * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* ─── Correlated metrics ──────────────────────────────────── */}
      {context?.correlated_anomalies?.length > 0 && (
        <div className="bg-surface-elevated rounded-theme-md p-3">
          <h4 className="text-xs font-semibold text-text-tertiary uppercase mb-3 flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Correlated Anomalies ({context.correlated_anomalies.length})
          </h4>
          <div className="space-y-1">
            {context.correlated_anomalies.map((metric: string, i: number) => (
              <div key={i} className="text-sm text-text-secondary px-2 py-1 bg-surface rounded">
                {metric}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* ─── Value context ───────────────────────────────────────── */}
      <div className="bg-surface-elevated rounded-theme-md p-3">
        <h4 className="text-xs font-semibold text-text-tertiary uppercase mb-3">Context</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><span className="text-text-tertiary">Value:</span> <span className="text-text font-mono">{context?.value?.toFixed(2)}</span></div>
          <div><span className="text-text-tertiary">Source:</span> <span className="text-text font-mono">{context?.source_id}</span></div>
          <div><span className="text-text-tertiary">Time:</span> <span className="text-text font-mono">{new Date(anomaly.timestamp).toLocaleString()}</span></div>
          <div><span className="text-text-tertiary">Weighted Score:</span> <span className="text-text font-mono">{context?.weighted_score?.toFixed(3)}</span></div>
        </div>
      </div>
      
      {/* ─── Actions ─────────────────────────────────────────────── */}
      <div className="flex gap-2">
        <button className="theme-button-primary">Acknowledge</button>
        <button className="theme-button">View Source</button>
        <button className="theme-button">Create Incident</button>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: any) {
  return (
    <div className={cn(
      'bg-surface border border-border rounded-theme-md p-3',
      color === 'danger' && 'border-danger/30',
      color === 'warning' && 'border-warning/30',
      color === 'sky' && 'border-sky-500/30',
    )}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-text-tertiary uppercase">{label}</div>
          <div className="text-2xl font-bold text-text font-mono mt-1">{value}</div>
        </div>
        <div className={cn(
          'opacity-60',
          color === 'danger' && 'text-danger',
          color === 'warning' && 'text-warning',
          color === 'sky' && 'text-sky-400',
        )}>{icon}</div>
      </div>
    </div>
  );
}
