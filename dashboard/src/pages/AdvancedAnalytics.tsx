import { useState, useMemo } from 'react';
import { useSimulationStore } from '@/stores/simulationStore';
import { TimeRangeSelector } from '@/components/charts/TimeRangeSelector';
import { TrajectoryChartWrapper } from '@/components/charts/TrajectoryChartWrapper';
import { InteractiveHeatmap, HeatmapCell } from '@/components/charts/InteractiveHeatmap';
import { ThemedChart } from '@/components/charts/ThemedChart';
import { BarChart3, Map } from 'lucide-react';

export function AdvancedAnalytics() {
  const detections = useSimulationStore((s) => s.detections);
  const robots = useSimulationStore((s) => Array.from(s.robots.values()));
  
  const [timeRange, setTimeRange] = useState({ start: Date.now() - 3600_000, end: Date.now(), label: 'Last hour' });
  const [, setShowComparison] = useState(false);
  
  const trajectories = useMemo(() => {
    return robots.map((r) => ({
      id: r.id,
      name: r.name,
      color: undefined,
      points: Array.from({ length: 50 }, (_, i) => {
        const t = Date.now() - (50 - i) * 60_000;
        const angle = (i / 50) * Math.PI * 2;
        return {
          timestamp: t,
          position: [
            r.position.x + Math.cos(angle) * (3 + Math.random()),
            r.position.y + Math.sin(i / 5) * 0.5,
            r.position.z + Math.sin(angle) * (3 + Math.random()),
          ] as [number, number, number],
          velocity: Math.random() * 2,
          event: i === 0 ? ('start' as const) : i === 49 ? ('end' as const) : i % 10 === 0 ? ('capture' as const) : undefined,
        };
      }),
    }));
  }, [robots]);
  
  const heatmapData = useMemo(() => {
    const grid: HeatmapCell[][] = Array.from({ length: 7 }, (_, day) =>
      Array.from({ length: 24 }, (_, hour) => {
        const count = detections.filter((d) => {
          const date = new Date(d.timestamp);
          return date.getDay() === day && date.getHours() === hour;
        }).length;
        return { row: day, col: hour, value: count, metadata: { day, hour } };
      })
    );
    return grid;
  }, [detections]);
  
  const sensorData = useMemo(() => {
    return Array.from({ length: 60 }, (_, i) => ({
      ts: Date.now() - (60 - i) * 60_000,
      co2: 400 + Math.sin(i / 10) * 50 + Math.random() * 20,
      temp: 22 + Math.sin(i / 15) * 3 + Math.random() * 1,
      humidity: 50 + Math.cos(i / 8) * 10 + Math.random() * 5,
    }));
  }, []);
  
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-primary-500" />
            Advanced Analytics & 3D Spatial Trajectories
          </h1>
          <p className="text-text-secondary text-sm mt-1">Theme-adaptive visualization components and interactive spatio-temporal data</p>
        </div>
      </div>
      
      <div className="bg-surface border border-border rounded-theme-lg p-3">
        <TimeRangeSelector
          value={timeRange}
          onChange={setTimeRange}
          showComparison
          onComparisonChange={setShowComparison}
        />
      </div>
      
      <div className="bg-surface border border-border rounded-theme-lg p-4">
        <h2 className="text-lg font-semibold text-text mb-3 flex items-center gap-2">
          <Map className="w-5 h-5 text-primary-500" />
          Robot Trajectories (3D Spatial Path Inspector)
        </h2>
        <TrajectoryChartWrapper data={trajectories} />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ThemedChart
          type="line"
          data={sensorData}
          xKey="ts"
          series={[
            { key: 'co2', name: 'CO₂ (ppm)' },
            { key: 'temp', name: 'Temperature (°C)' },
          ]}
          height={300}
          formatX={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        />
        <ThemedChart
          type="area"
          data={sensorData}
          xKey="ts"
          series={[
            { key: 'humidity', name: 'Humidity (%)' },
          ]}
          height={300}
          formatX={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        />
      </div>
      
      <InteractiveHeatmap
        data={heatmapData}
        rowLabels={['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']}
        colLabels={Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'))}
        title="Detection Activity Heatmap (Day × Hour)"
        colorScale="thermal"
        onCellClick={(cell) => console.log('Clicked heatmap cell:', cell)}
      />
    </div>
  );
}
