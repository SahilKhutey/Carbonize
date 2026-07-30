import { useQuery } from '@tanstack/react-query';
import { Activity, Wind, Thermometer, Droplets, Zap, Cpu } from 'lucide-react';
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart';
import { StatCard } from '@/components/charts/StatCard';
import { useSimulationStore } from '@/stores/simulationStore';
import { robotsApi } from '@/lib/api';

export function TelemetryOverview() {
  const simState = useSimulationStore((s) => s.simState);
  const recentTelemetry = useSimulationStore((s) => s.recentTelemetry);

  const { data: robots = [] } = useQuery({
    queryKey: ['robots'],
    queryFn: () => robotsApi.list(),
    refetchInterval: 5000,
  });

  const onlineRobots = robots.filter((r) => r.status !== 'offline').length;
  const avgBattery = robots.length > 0
    ? robots.reduce((acc, r) => acc + r.battery, 0) / robots.length
    : 0;

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Telemetry Overview</h1>
          <p className="text-slate-400 text-sm mt-1">Real-time system status and metrics</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <div className="w-2 h-2 rounded-full bg-carbon-400 animate-pulse" />
          Live updating
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="CO₂ Concentration"
          value={simState?.environment.co2Concentration.toFixed(0) ?? '—'}
          unit="ppm"
          icon={<Wind className="w-8 h-8" />}
          color="carbon"
        />
        <StatCard
          label="Temperature"
          value={simState?.environment.temperature.toFixed(1) ?? '—'}
          unit="°C"
          icon={<Thermometer className="w-8 h-8" />}
          color="warning"
        />
        <StatCard
          label="Humidity"
          value={simState?.environment.humidity.toFixed(0) ?? '—'}
          unit="%"
          icon={<Droplets className="w-8 h-8" />}
          color="sky"
        />
        <StatCard
          label="Active Robots"
          value={`${onlineRobots}/${robots.length}`}
          icon={<Activity className="w-8 h-8" />}
          color="carbon"
        />
        <StatCard
          label="Avg Battery"
          value={avgBattery.toFixed(0)}
          unit="%"
          icon={<Zap className="w-8 h-8" />}
          color={avgBattery > 50 ? 'carbon' : avgBattery > 20 ? 'warning' : 'critical'}
        />
        <StatCard
          label="Sim Speed"
          value={simState?.speedFactor.toFixed(1) ?? '1.0'}
          unit="x"
          icon={<Cpu className="w-8 h-8" />}
          color="neutral"
        />
        <StatCard
          label="Total Detections"
          value={useSimulationStore.getState().detections.length}
          icon={<Activity className="w-8 h-8" />}
          color="carbon"
        />
        <StatCard
          label="Sim Time"
          value={simState?.currentTime.toFixed(0) ?? '0'}
          unit="s"
          icon={<Activity className="w-8 h-8" />}
          color="neutral"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TimeSeriesChart
          data={recentTelemetry}
          title="CO₂ Concentration (live)"
          unit="ppm"
          color="#22c55e"
          height={250}
          yDomain={['auto', 'auto']}
        />
        <TimeSeriesChart
          data={recentTelemetry.map((t) => ({ ts: t.ts, value: t.value * 0.05 + 22 }))}
          title="Temperature Trend"
          unit="°C"
          color="#f59e0b"
          height={250}
        />
      </div>

      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <h2 className="text-lg font-semibold text-slate-200 mb-3">Robot Fleet</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {robots.map((robot) => (
            <div
              key={robot.id}
              className="bg-slate-800 rounded-lg p-3 border border-slate-700 hover:border-carbon-500/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-slate-200">{robot.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  robot.status === 'error' ? 'bg-critical-500/20 text-critical-400' :
                  robot.status === 'navigating' ? 'bg-sky-500/20 text-sky-400' :
                  robot.status === 'capturing' ? 'bg-carbon-500/20 text-carbon-400' :
                  'bg-slate-700 text-slate-400'
                }`}>
                  {robot.status}
                </span>
              </div>
              <div className="text-xs text-slate-400 space-y-1">
                <div className="flex justify-between">
                  <span>Battery:</span>
                  <span className={`font-mono ${robot.battery < 20 ? 'text-critical-400' : 'text-slate-200'}`}>
                    {robot.battery.toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Position:</span>
                  <span className="font-mono text-slate-300">
                    {robot.position.x.toFixed(1)}, {robot.position.y.toFixed(1)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
