import { useQuery, useMutation } from '@tanstack/react-query';
import { FlaskConical, Play, Square, BarChart3 } from 'lucide-react';
import { experimentsApi } from '@/lib/api';
import { cn } from '@/lib/utils';

export function Experiments() {
  const { data: experiments = [] } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => experimentsApi.list(),
  });

  const startMutation = useMutation({
    mutationFn: experimentsApi.start,
  });

  const stopMutation = useMutation({
    mutationFn: experimentsApi.stop,
  });

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FlaskConical className="w-7 h-7 text-carbon-400" />
          A/B Experiments
        </h1>
        <p className="text-slate-400 text-sm mt-1">Statistical comparison of model variants in production</p>
      </div>

      <div className="space-y-3">
        {experiments.map((exp) => (
          <div key={exp.id} className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-slate-200">{exp.name}</h3>
                <p className="text-xs text-slate-500 mt-1">{exp.description}</p>
              </div>
              <span className={cn('text-xs px-2 py-1 rounded-full',
                exp.status === 'running' ? 'bg-carbon-500/20 text-carbon-400' :
                exp.status === 'completed' ? 'bg-sky-500/20 text-sky-400' :
                'bg-slate-700 text-slate-300'
              )}>
                {exp.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              {exp.variants.map((v) => (
                <div key={v.name} className="bg-slate-800 rounded p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-200 text-sm">
                      {v.name}
                      {v.isControl && <span className="ml-2 text-xs text-slate-500">(control)</span>}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">{(v.trafficWeight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                    <div><span className="text-slate-500">Samples:</span> <span className="text-slate-200 font-mono">{v.samples}</span></div>
                    <div><span className="text-slate-500">Latency:</span> <span className="text-slate-200 font-mono">{v.metrics.avgLatencyMs.toFixed(1)}ms</span></div>
                    <div><span className="text-slate-500">Success:</span> <span className="text-slate-200 font-mono">{(v.metrics.successRate * 100).toFixed(1)}%</span></div>
                  </div>
                </div>
              ))}
            </div>

            {exp.results && (
              <div className="bg-slate-800 rounded p-3 mb-3">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="w-4 h-4 text-carbon-400" />
                  <span className="text-sm font-semibold text-slate-200">Statistical Results</span>
                </div>
                <div className="grid grid-cols-4 gap-3 text-xs">
                  <div><span className="text-slate-500">p-value:</span> <span className="text-slate-200 font-mono">{exp.results.pValue.toFixed(4)}</span></div>
                  <div><span className="text-slate-500">Effect size:</span> <span className="text-slate-200 font-mono">{exp.results.effectSize.toFixed(3)}</span></div>
                  <div><span className="text-slate-500">95% CI:</span> <span className="text-slate-200 font-mono">[{exp.results.confidenceInterval[0].toFixed(3)}, {exp.results.confidenceInterval[1].toFixed(3)}]</span></div>
                  <div><span className="text-slate-500">Winner:</span> <span className="text-carbon-400 font-mono">{exp.results.winner ?? '—'}</span></div>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              {exp.status === 'draft' && (
                <button
                  onClick={() => startMutation.mutate(exp.id)}
                  className="flex items-center gap-1 px-3 py-1 bg-carbon-500/20 text-carbon-400 rounded hover:bg-carbon-500/30 text-sm"
                >
                  <Play className="w-3 h-3" />
                  Start
                </button>
              )}
              {exp.status === 'running' && (
                <button
                  onClick={() => stopMutation.mutate(exp.id)}
                  className="flex items-center gap-1 px-3 py-1 bg-critical-500/20 text-critical-400 rounded hover:bg-critical-500/30 text-sm"
                >
                  <Square className="w-3 h-3" />
                  Stop
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
