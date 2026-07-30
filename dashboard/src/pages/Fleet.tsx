import { useQuery } from '@tanstack/react-query';
import { Bot, Battery, MapPin, Send, RefreshCw } from 'lucide-react';
import { robotsApi } from '@/lib/api';
import { useSimulationStore } from '@/stores/simulationStore';
import { cn } from '@/lib/utils';

export function Fleet() {
  const { data: robots = [] } = useQuery({
    queryKey: ['robots'],
    queryFn: () => robotsApi.list(),
    refetchInterval: 3000,
  });
  const selectedId = useSimulationStore((s) => s.selectedRobotId);
  const setSelected = useSimulationStore((s) => s.setSelectedRobot);
  const selected = robots.find((r) => r.id === selectedId);

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Bot className="w-7 h-7 text-carbon-400" />
          Robot Fleet
        </h1>
        <p className="text-slate-400 text-sm mt-1">Manage and dispatch robots for carbon capture missions</p>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-4 space-y-2 max-h-[calc(100vh-180px)] overflow-y-auto">
          {robots.map((r) => (
            <button
              key={r.id}
              onClick={() => setSelected(r.id)}
              className={cn(
                'w-full text-left bg-slate-900 rounded-lg p-3 border transition-colors',
                selectedId === r.id ? 'border-carbon-500' : 'border-slate-800 hover:border-slate-700'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="font-semibold text-slate-200">{r.name}</div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded-full',
                  r.status === 'error' ? 'bg-critical-500/20 text-critical-400' :
                  r.status === 'navigating' ? 'bg-sky-500/20 text-sky-400' :
                  r.status === 'capturing' ? 'bg-carbon-500/20 text-carbon-400' :
                  'bg-slate-700 text-slate-400'
                )}>
                  {r.status}
                </span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1 text-slate-400">
                  <Battery className="w-3 h-3" />
                  <span className={cn('font-mono', r.battery < 20 ? 'text-critical-400' : 'text-slate-200')}>
                    {r.battery.toFixed(0)}%
                  </span>
                </div>
                <div className="flex items-center gap-1 text-slate-400">
                  <MapPin className="w-3 h-3" />
                  <span className="font-mono text-slate-200">{r.position.x.toFixed(1)}, {r.position.y.toFixed(1)}</span>
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="col-span-8 bg-slate-900 rounded-lg border border-slate-800 p-6">
          {selected ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-100">{selected.name}</h2>
                  <p className="text-sm text-slate-500 mt-1">ID: {selected.id}</p>
                </div>
                <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 text-sm">
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <Stat label="Status" value={selected.status} />
                <Stat label="Battery" value={`${selected.battery.toFixed(0)}%`} />
                <Stat label="Current Task" value={selected.currentTask ?? 'Idle'} />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <Stat label="X" value={selected.position.x.toFixed(2)} />
                <Stat label="Y" value={selected.position.y.toFixed(2)} />
                <Stat label="Z" value={selected.position.z.toFixed(2)} />
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Commands</h3>
                <div className="grid grid-cols-2 gap-2">
                  {['Go Home', 'Start Capture', 'Pause', 'Resume', 'Return to Base', 'Emergency Stop'].map((cmd) => (
                    <button
                      key={cmd}
                      onClick={() => robotsApi.sendCommand(selected.id, cmd.toLowerCase().replace(' ', '_'))}
                      className={cn(
                        'flex items-center justify-center gap-2 px-3 py-2 rounded text-sm font-medium',
                        cmd === 'Emergency Stop'
                          ? 'bg-critical-500/20 text-critical-400 hover:bg-critical-500/30'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      )}
                    >
                      <Send className="w-3 h-3" />
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-12">
              <Bot className="w-12 h-12 mx-auto opacity-30 mb-3" />
              Select a robot to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-lg p-3">
      <div className="text-xs text-slate-500 uppercase">{label}</div>
      <div className="text-lg font-semibold text-slate-200 mt-1 font-mono">{value}</div>
    </div>
  );
}
