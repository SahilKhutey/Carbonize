import { useMemo } from 'react';
import { BarChart3, TrendingUp, Map, Calendar } from 'lucide-react';
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart';
import { StatCard } from '@/components/charts/StatCard';
import { HeatmapGrid } from '@/components/charts/HeatmapGrid';
import { useSimulationStore } from '@/stores/simulationStore';

export function Analytics() {
  const detections = useSimulationStore((s) => s.detections);
  const robots = useSimulationStore((s) => Array.from(s.robots.values()));

  const classCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    detections.forEach((d) => { counts[d.class] = (counts[d.class] || 0) + 1; });
    return counts;
  }, [detections]);

  const hourlyData = useMemo(() => {
    const hours: Record<number, number> = {};
    detections.forEach((d) => {
      const h = new Date(d.timestamp).getHours();
      hours[h] = (hours[h] || 0) + 1;
    });
    return Array.from({ length: 24 }, (_, h) => ({
      ts: Date.now() - (23 - h) * 3600_000,
      value: hours[h] || 0,
    }));
  }, [detections]);

  const heatmapData = useMemo(() => {
    const grid = Array.from({ length: 7 }, () => Array(24).fill(0));
    detections.forEach((d) => {
      const date = new Date(d.timestamp);
      const day = date.getDay();
      const hour = date.getHours();
      grid[day][hour] += 1;
    });
    return grid;
  }, [detections]);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-7 h-7 text-carbon-400" />
          CO₂ Capture Analytics
        </h1>
        <p className="text-slate-400 text-sm mt-1">Insights, trends, and performance indicators</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Total Captured" value={(detections.length * 1.2).toFixed(1)} unit="kg CO₂" trend={15.2} icon={<TrendingUp className="w-8 h-8" />} color="carbon" />
        <StatCard label="Total Detections" value={detections.length} icon={<BarChart3 className="w-8 h-8" />} color="carbon" />
        <StatCard label="Active Robots" value={robots.filter((r) => r.status !== 'offline').length} icon={<Map className="w-8 h-8" />} color="sky" />
        <StatCard label="Uptime" value="99.7" unit="%" trend={0.3} icon={<Calendar className="w-8 h-8" />} color="carbon" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TimeSeriesChart data={hourlyData} title="Detections per Hour" color="#0ea5e9" height={250} />
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Detections by Class</h3>
          <div className="space-y-2">
            {Object.entries(classCounts).map(([cls, count]) => {
              const max = Math.max(...Object.values(classCounts), 1);
              const pct = (count / max) * 100;
              return (
                <div key={cls}>
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>{cls}</span>
                    <span className="font-mono">{count}</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-carbon-500 to-sky-500" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Activity Heatmap (Day × Hour)</h3>
        <HeatmapGrid
          data={heatmapData}
          labels={{
            y: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            x: Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0')),
          }}
        />
      </div>
    </div>
  );
}
