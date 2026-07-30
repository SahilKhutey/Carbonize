import { useState } from 'react';
import { ThemedChart } from '@/components/charts/ThemedChart';
import { useTheme } from '@/themes/ThemeProvider';
import type { PerClassMetrics as PerClassMetricsType } from '@/ml/types';
import { cn } from '@/lib/utils';

export function PerClassMetrics({ metrics }: { metrics: PerClassMetricsType[] }) {
  const { theme } = useTheme();
  const [sortBy, setSortBy] = useState<'f1Score' | 'support' | 'className'>('f1Score');
  
  const sorted = [...metrics].sort((a, b) => {
    if (sortBy === 'className') return a.className.localeCompare(b.className);
    return (b[sortBy] as number) - (a[sortBy] as number);
  });
  
  const chartData = sorted.map((m) => ({
    class: m.className,
    precision: m.precision,
    recall: m.recall,
    f1Score: m.f1Score,
  }));
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">Per-Class Performance</h3>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="bg-surface-elevated text-text text-xs rounded-theme-md px-2 py-1 border border-border"
        >
          <option value="f1Score">Sort by F1</option>
          <option value="support">Sort by support</option>
          <option value="className">Sort by name</option>
        </select>
      </div>
      
      <ThemedChart
        type="bar"
        data={chartData}
        xKey="class"
        series={[
          { key: 'precision', name: 'Precision', color: theme.colors.chart1 },
          { key: 'recall', name: 'Recall', color: theme.colors.chart2 },
          { key: 'f1Score', name: 'F1', color: theme.colors.chart3 },
        ]}
        height={300}
        formatY={(v) => (v * 100).toFixed(0) + '%'}
      />
      
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-text-tertiary border-b border-border">
              <th className="text-left p-1.5">Class</th>
              <th className="text-right p-1.5">Precision</th>
              <th className="text-right p-1.5">Recall</th>
              <th className="text-right p-1.5">F1 Score</th>
              <th className="text-right p-1.5">Support</th>
              <th className="text-right p-1.5">TP</th>
              <th className="text-right p-1.5">FP</th>
              <th className="text-right p-1.5">FN</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((m) => (
              <tr key={m.className} className="hover:bg-surface-hover border-b border-border-muted">
                <td className="p-1.5 text-text font-mono font-medium">{m.className}</td>
                <td className="p-1.5 text-right text-text font-mono">{(m.precision * 100).toFixed(1)}%</td>
                <td className="p-1.5 text-right text-text font-mono">{(m.recall * 100).toFixed(1)}%</td>
                <td className={cn(
                  'p-1.5 text-right font-mono font-bold',
                  m.f1Score > 0.85 ? 'text-success' : m.f1Score > 0.7 ? 'text-text' : 'text-warning'
                )}>
                  {(m.f1Score * 100).toFixed(1)}%
                </td>
                <td className="p-1.5 text-right text-text-secondary font-mono">{m.support}</td>
                <td className="p-1.5 text-right text-success font-mono">{m.tp}</td>
                <td className="p-1.5 text-right text-warning font-mono">{m.fp}</td>
                <td className="p-1.5 text-right text-danger font-mono">{m.fn}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
