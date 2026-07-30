import { useTheme } from '@/themes/ThemeProvider';
import { ThemedChart } from '@/components/charts/ThemedChart';
import type { AblationResult } from '@/ml/types';
import { Check, X } from 'lucide-react';

export function AblationStudy({ results }: { results: AblationResult[] }) {
  const { theme } = useTheme();
  
  const allFeatures = Array.from(
    new Set(results.flatMap((r) => Object.keys(r.features)))
  );
  
  const data = results.map((r) => ({
    config: r.configName,
    mAP50: r.metrics.mAP50,
    mAP50_95: r.metrics.mAP50_95,
    latency: r.metrics.latencyMs,
  }));
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4 space-y-4">
      <h3 className="text-sm font-semibold text-text">Ablation Study Matrix</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-text-tertiary border-b border-border">
              <th className="text-left p-2">Configuration</th>
              {allFeatures.map((f) => (
                <th key={f} className="p-2 text-center capitalize">{f.replace('_', ' ')}</th>
              ))}
              <th className="p-2 text-right">mAP50</th>
              <th className="p-2 text-right">mAP50-95</th>
              <th className="p-2 text-right">Latency</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.configName} className="hover:bg-surface-hover border-b border-border-muted">
                <td className="p-2 text-text font-mono font-medium">{r.configName}</td>
                {allFeatures.map((f) => (
                  <td key={f} className="p-2 text-center">
                    {r.features[f] ? (
                      <Check className="w-4 h-4 text-success inline" />
                    ) : (
                      <X className="w-4 h-4 text-danger inline" />
                    )}
                  </td>
                ))}
                <td className="p-2 text-right text-text font-mono font-bold">{(r.metrics.mAP50 * 100).toFixed(1)}%</td>
                <td className="p-2 text-right text-text font-mono">{(r.metrics.mAP50_95 * 100).toFixed(1)}%</td>
                <td className="p-2 text-right text-text-secondary font-mono">{r.metrics.latencyMs.toFixed(1)}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <ThemedChart
        type="bar"
        data={data}
        xKey="config"
        series={[{ key: 'mAP50', name: 'mAP50', color: theme.colors.chart1 }]}
        height={250}
        formatY={(v) => (v * 100).toFixed(0) + '%'}
      />
    </div>
  );
}
