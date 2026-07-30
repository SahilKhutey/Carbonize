import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import { ThemedChart } from '@/components/charts/ThemedChart';
import { useTheme } from '@/themes/ThemeProvider';
import { mlAnalyticsApi } from '@/ml/api';
import { cn } from '@/lib/utils';

export function DriftMonitor() {
  const { theme } = useTheme();
  const [referenceWindow] = useState({
    start: Date.now() - 7 * 86_400_000,
    end: Date.now() - 86_400_000,
  });
  const [testWindow] = useState({
    start: Date.now() - 86_400_000,
    end: Date.now(),
  });
  
  const { data: driftReport, isLoading } = useQuery({
    queryKey: ['drift', referenceWindow, testWindow],
    queryFn: () => mlAnalyticsApi.getDataDrift({ referenceWindow, testWindow, method: 'ks_test' }),
    refetchInterval: 60_000,
  });
  
  const { data: conceptDrift } = useQuery({
    queryKey: ['concept-drift', '1.5.0'],
    queryFn: () => mlAnalyticsApi.getConceptDrift('1.5.0', 'eddm'),
    refetchInterval: 60_000,
  });
  
  if (isLoading || !driftReport) {
    return <div className="animate-pulse h-64 bg-surface rounded-theme-md" />;
  }
  
  const statusColor = driftReport.detection === 'drift_detected' ? 'danger' : 
                     driftReport.detection === 'warning' ? 'warning' : 'success';
  const statusIcon = driftReport.detection === 'drift_detected' ? AlertTriangle : 
                    driftReport.detection === 'warning' ? Activity : CheckCircle;
  const StatusIcon = statusIcon;
  
  return (
    <div className="space-y-4">
      <div className={cn(
        'p-4 rounded-theme-md border flex items-center gap-3',
        statusColor === 'success' && 'bg-success/10 border-success/30',
        statusColor === 'warning' && 'bg-warning/10 border-warning/30',
        statusColor === 'danger' && 'bg-danger/10 border-danger/30',
      )}>
        <StatusIcon className={cn(
          'w-6 h-6',
          statusColor === 'success' && 'text-success',
          statusColor === 'warning' && 'text-warning',
          statusColor === 'danger' && 'text-danger',
        )} />
        <div className="flex-1">
          <div className="font-semibold text-text">
            {driftReport.detection === 'drift_detected' ? 'Data drift detected' :
             driftReport.detection === 'warning' ? 'Minor drift detected' :
             'No drift detected'}
          </div>
          <div className="text-sm text-text-secondary">
            {driftReport.features.filter((f) => f.isDrifted).length} of {driftReport.features.length} features show drift
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-text-tertiary">Overall Score</div>
          <div className="text-2xl font-bold font-mono text-text">
            {(driftReport.overallScore * 100).toFixed(0)}%
          </div>
        </div>
      </div>
      
      <div className="bg-surface border border-border rounded-theme-md p-4">
        <h3 className="text-sm font-semibold text-text mb-3">Per-Feature Drift Score</h3>
        <div className="space-y-2">
          {driftReport.features.map((feature) => (
            <div key={feature.name} className="flex items-center gap-3">
              <div className="w-32 text-xs text-text-secondary font-mono">{feature.name}</div>
              <div className="flex-1 h-3 bg-surface-elevated rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full transition-all',
                    feature.isDrifted ? 'bg-danger' : 'bg-success'
                  )}
                  style={{ width: `${feature.driftScore * 100}%` }}
                />
              </div>
              <div className="w-16 text-right text-xs font-mono text-text">
                {(feature.driftScore * 100).toFixed(0)}%
              </div>
              {feature.pValue !== undefined && (
                <div className="w-20 text-right text-xs text-text-tertiary font-mono">
                  p={feature.pValue.toFixed(3)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {driftReport.features.slice(0, 4).map((feature) => (
          <ThemedChart
            key={feature.name}
            type="area"
            data={feature.referenceDistribution.map((v, i) => ({
              ts: i,
              ref: v,
              test: feature.testDistribution[i] || 0,
            }))}
            series={[
              { key: 'ref', name: 'Reference', color: theme.colors.chart2 },
              { key: 'test', name: 'Test', color: feature.isDrifted ? theme.colors.danger[500] : theme.colors.success[500] },
            ]}
            xKey="ts"
            title={`${feature.name} distribution`}
            height={200}
          />
        ))}
      </div>
      
      {conceptDrift && (
        <div className="bg-surface border border-border rounded-theme-md p-4">
          <h3 className="text-sm font-semibold text-text mb-3">Concept Drift Monitor</h3>
          <div className="grid grid-cols-3 gap-3">
            <MetricBox label="Detection" value={conceptDrift.detection} color={conceptDrift.detection === 'drift_detected' ? 'danger' : 'success'} />
            <MetricBox label="Error Rate" value={conceptDrift.errorRate.toFixed(3)} />
            <MetricBox label="Baseline" value={conceptDrift.baselineErrorRate.toFixed(3)} />
          </div>
        </div>
      )}
    </div>
  );
}

function MetricBox({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-surface-elevated rounded-theme-md p-3">
      <div className="text-xs text-text-tertiary">{label}</div>
      <div className={cn(
        'text-lg font-bold font-mono mt-1 text-text',
        color === 'danger' && 'text-danger',
        color === 'success' && 'text-success',
      )}>{value}</div>
    </div>
  );
}
