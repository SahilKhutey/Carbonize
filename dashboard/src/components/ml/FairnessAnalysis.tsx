import type { FairnessMetrics } from '@/ml/types';
import { ThemedChart } from '@/components/charts/ThemedChart';
import { cn } from '@/lib/utils';

export function FairnessAnalysis({ metrics }: { metrics: FairnessMetrics }) {
  const data = metrics.groups.map((g) => ({
    group: g.groupName,
    positiveRate: g.positiveRate,
    tpr: g.truePositiveRate,
    precision: g.precision,
  }));
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4 space-y-4">
      <h3 className="text-sm font-semibold text-text">
        Fairness Analysis: Protected Attribute ({metrics.protectedAttribute})
      </h3>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <FairnessMetric label="Demographic Parity" value={metrics.metrics.demographicParity} threshold={0.1} />
        <FairnessMetric label="Equalized Odds" value={metrics.metrics.equalizedOdds} threshold={0.1} />
        <FairnessMetric label="Equal Opportunity" value={metrics.metrics.equalOpportunity} threshold={0.1} />
        <FairnessMetric label="Predictive Parity" value={metrics.metrics.predictiveParity} threshold={0.1} />
      </div>
      
      <ThemedChart
        type="bar"
        data={data}
        xKey="group"
        series={[
          { key: 'positiveRate', name: 'Positive Rate' },
          { key: 'tpr', name: 'True Positive Rate' },
          { key: 'precision', name: 'Precision' },
        ]}
        height={300}
        formatY={(v) => (v * 100).toFixed(0) + '%'}
      />
    </div>
  );
}

function FairnessMetric({ label, value, threshold }: { label: string; value: number; threshold: number }) {
  const passed = value < threshold;
  return (
    <div className="bg-surface-elevated border border-border rounded-theme-md p-3">
      <div className="text-xs text-text-tertiary font-medium">{label}</div>
      <div className={cn(
        'text-lg font-bold font-mono mt-1',
        passed ? 'text-success' : 'text-danger'
      )}>
        {value.toFixed(3)}
      </div>
      <div className="text-xs text-text-secondary mt-1">
        {passed ? '✓ Fair' : '✗ Biased'} (threshold: {threshold})
      </div>
    </div>
  );
}
