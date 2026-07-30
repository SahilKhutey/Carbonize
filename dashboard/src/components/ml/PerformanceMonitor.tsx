import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ThemedChart } from '@/components/charts/ThemedChart';
import { StatCard } from '@/components/charts/StatCard';
import { mlAnalyticsApi } from '@/ml/api';
import { TimeRangeSelector } from '@/components/charts/TimeRangeSelector';
import { Activity, Cpu, Zap, Clock } from 'lucide-react';

export function PerformanceMonitor() {
  const [timeRange, setTimeRange] = useState({
    start: Date.now() - 24 * 3600_000,
    end: Date.now(),
    label: 'Last 24 hours',
  });
  
  const { data: history = [] } = useQuery({
    queryKey: ['performance-history', timeRange],
    queryFn: () => mlAnalyticsApi.getPerformanceMetrics({ from: timeRange.start, to: timeRange.end }),
  });
  
  const latest = history[history.length - 1];
  
  if (!latest) return <div className="animate-pulse h-64 bg-surface rounded-theme-md" />;
  
  return (
    <div className="space-y-4">
      <div className="bg-surface border border-border rounded-theme-md p-3">
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="mAP50" value={(latest.mAP50 * 100).toFixed(1)} unit="%" icon={<Activity className="w-8 h-8" />} color="carbon" />
        <StatCard label="mAP50-95" value={(latest.mAP50_95 * 100).toFixed(1)} unit="%" icon={<Activity className="w-8 h-8" />} color="carbon" />
        <StatCard label="Precision" value={(latest.precision * 100).toFixed(1)} unit="%" icon={<Activity className="w-8 h-8" />} color="carbon" />
        <StatCard label="Recall" value={(latest.recall * 100).toFixed(1)} unit="%" icon={<Activity className="w-8 h-8" />} color="carbon" />
        <StatCard label="Inference Latency" value={latest.inferenceLatencyMs.toFixed(1)} unit="ms" icon={<Clock className="w-8 h-8" />} color="sky" />
        <StatCard label="Throughput" value={latest.throughputFps.toFixed(1)} unit="fps" icon={<Zap className="w-8 h-8" />} color="sky" />
        <StatCard label="GPU Util" value={latest.gpuUtilization.toFixed(0)} unit="%" icon={<Cpu className="w-8 h-8" />} color="warning" />
        <StatCard label="Memory" value={(latest.memoryUsageMb / 1024).toFixed(1)} unit="GB" icon={<Cpu className="w-8 h-8" />} color="warning" />
      </div>
      
      <ThemedChart
        type="line"
        data={history.map((h) => ({ ts: h.timestamp, ...h }))}
        xKey="ts"
        series={[
          { key: 'mAP50', name: 'mAP50' },
          { key: 'mAP50_95', name: 'mAP50-95' },
        ]}
        height={300}
        formatX={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        formatY={(v) => (v * 100).toFixed(0) + '%'}
      />
      
      <ThemedChart
        type="area"
        data={history.map((h) => ({ ts: h.timestamp, ...h }))}
        xKey="ts"
        series={[
          { key: 'inferenceLatencyMs', name: 'Latency (ms)' },
        ]}
        height={250}
        formatX={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      />
    </div>
  );
}
