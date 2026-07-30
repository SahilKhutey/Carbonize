import { useState } from 'react';
import { Play, Pause, Square, SkipForward, Settings, FlaskConical } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SceneViewer } from '@/components/scene/SceneViewer';
import { simulationApi } from '@/lib/api';
import { useSimulationStore } from '@/stores/simulationStore';
import { cn } from '@/lib/utils';

const SCENARIOS = [
  { id: 'baseline', name: 'Baseline Capture', description: 'Standard carbon capture operation', duration: 300 },
  { id: 'high_emission', name: 'High Emission Event', description: 'CO₂ release from industrial site', duration: 600 },
  { id: 'multi_robot', name: 'Multi-Robot Coordination', description: '3 robots working together', duration: 900 },
  { id: 'dom_rand', name: 'Domain Randomization Stress', description: 'Extreme weather conditions', duration: 1200 },
  { id: 'fault_recovery', name: 'Fault Recovery', description: 'Robot failure scenarios', duration: 600 },
];

export function Simulation() {
  const simState = useSimulationStore((s) => s.simState);
  const queryClient = useQueryClient();
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [speed, setSpeed] = useState(1.0);

  const startMutation = useMutation({
    mutationFn: simulationApi.start,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['simState'] }),
  });
  const pauseMutation = useMutation({ mutationFn: simulationApi.pause });
  const stopMutation = useMutation({ mutationFn: simulationApi.stop });
  const stepMutation = useMutation({ mutationFn: simulationApi.step });

  const setSpeedMutation = useMutation({
    mutationFn: (s: number) => simulationApi.setSpeed(s),
    onSuccess: () => setSpeed(speed),
  });

  return (
    <div className="flex h-full">
      <div className="w-80 bg-slate-900 border-r border-slate-800 p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <FlaskConical className="w-5 h-5 text-carbon-400" />
          Simulation Control
        </h2>

        <div className="bg-slate-800 rounded-lg p-3 mb-4">
          <div className="grid grid-cols-4 gap-2 mb-3">
            <button
              onClick={() => startMutation.mutate({ scenarios: selectedScenario ? [selectedScenario] : [], speed })}
              disabled={simState?.status === 'running'}
              className="flex items-center justify-center p-2 bg-carbon-500/20 text-carbon-400 rounded hover:bg-carbon-500/30 disabled:opacity-50"
              title="Play"
            >
              <Play className="w-4 h-4" />
            </button>
            <button
              onClick={() => pauseMutation.mutate()}
              disabled={simState?.status !== 'running'}
              className="flex items-center justify-center p-2 bg-sky-500/20 text-sky-400 rounded hover:bg-sky-500/30 disabled:opacity-50"
              title="Pause"
            >
              <Pause className="w-4 h-4" />
            </button>
            <button
              onClick={() => stepMutation.mutate()}
              disabled={simState?.status !== 'paused'}
              className="flex items-center justify-center p-2 bg-slate-700 text-slate-300 rounded hover:bg-slate-600 disabled:opacity-50"
              title="Step"
            >
              <SkipForward className="w-4 h-4" />
            </button>
            <button
              onClick={() => stopMutation.mutate()}
              className="flex items-center justify-center p-2 bg-critical-500/20 text-critical-400 rounded hover:bg-critical-500/30"
              title="Stop"
            >
              <Square className="w-4 h-4" />
            </button>
          </div>

          <div className="text-xs text-slate-400 mb-1">
            Speed: <span className="text-carbon-400 font-mono">{speed.toFixed(1)}x</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            onMouseUp={() => setSpeedMutation.mutate(speed)}
            className="w-full accent-carbon-500"
          />
        </div>

        <div className="bg-slate-800 rounded-lg p-3 mb-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-2">Scenarios</h3>
          <div className="space-y-2">
            {SCENARIOS.map((s) => (
              <button
                key={s.id}
                onClick={() => setSelectedScenario(selectedScenario === s.id ? null : s.id)}
                className={cn(
                  'w-full text-left p-2 rounded border transition-colors',
                  selectedScenario === s.id
                    ? 'bg-carbon-500/20 border-carbon-500/40 text-carbon-400'
                    : 'bg-slate-700 border-slate-600 hover:bg-slate-600 text-slate-300'
                )}
              >
                <div className="text-sm font-medium">{s.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{s.description}</div>
                <div className="text-xs text-slate-500 mt-1 font-mono">⏱ {s.duration}s</div>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Environment
          </h3>
          <EnvironmentSlider label="CO₂ Level" value={simState?.environment.co2Concentration ?? 400} max={2000} color="carbon" />
          <EnvironmentSlider label="Temperature" value={simState?.environment.temperature ?? 22} max={40} color="warning" />
          <EnvironmentSlider label="Humidity" value={simState?.environment.humidity ?? 50} max={100} color="sky" />
          <EnvironmentSlider label="Light Intensity" value={simState?.environment.lightIntensity ?? 1} max={2} step={0.1} color="warning" />
          <EnvironmentSlider label="Wind" value={simState?.environment.windSpeed ?? 0} max={20} color="sky" />
        </div>
      </div>

      <div className="flex-1 relative">
        <SceneViewer />

        <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur rounded-lg p-3 text-xs space-y-1 min-w-48 border border-slate-800">
          <div className="font-semibold text-carbon-400">Live Status</div>
          <Row label="Status" value={simState?.status ?? 'idle'} />
          <Row label="Sim Time" value={`${simState?.currentTime.toFixed(1) ?? '0.0'}s`} />
          <Row label="Real Time" value={`${simState?.realTime.toFixed(1) ?? '0.0'}s`} />
          <Row label="Speed" value={`${simState?.speedFactor.toFixed(2) ?? '1.00'}x`} />
          {selectedScenario && (
            <Row label="Scenario" value={SCENARIOS.find((s) => s.id === selectedScenario)?.name ?? '—'} />
          )}
        </div>
      </div>
    </div>
  );
}

function EnvironmentSlider({ label, value, max, step = 1, color }: { label: string; value: number; max: number; step?: number; color: 'carbon' | 'sky' | 'warning' }) {
  const accentColor = color === 'carbon' ? 'accent-carbon-500' : color === 'sky' ? 'accent-sky-500' : 'accent-warning-500';
  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className="font-mono text-slate-200">{value.toFixed(step < 1 ? 1 : 0)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={max}
        step={step}
        defaultValue={value}
        className={cn('w-full', accentColor)}
      />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-400">{label}:</span>
      <span className="text-slate-200 font-mono">{value}</span>
    </div>
  );
}
