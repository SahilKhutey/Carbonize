import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Brain, Upload, GitBranch, Rocket, Archive } from 'lucide-react';
import { modelsApi } from '@/lib/api';
import { cn } from '@/lib/utils';

const stageColors = {
  None: 'bg-slate-700 text-slate-300',
  Staging: 'bg-sky-500/20 text-sky-400',
  Production: 'bg-carbon-500/20 text-carbon-400',
  Archived: 'bg-slate-600/40 text-slate-500',
};

export function Models() {
  const queryClient = useQueryClient();
  const { data: models = [] } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelsApi.list(),
  });

  const promoteMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: string }) => modelsApi.promote(id, stage),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['models'] }),
  });

  const productionModel = models.find((m) => m.stage === 'Production');
  const stagingModels = models.filter((m) => m.stage === 'Staging');
  const archivedModels = models.filter((m) => m.stage === 'Archived' || m.stage === 'None');

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Brain className="w-7 h-7 text-carbon-400" />
            Model Registry
          </h1>
          <p className="text-slate-400 text-sm mt-1">MLflow-tracked versions with deployment stage management</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-carbon-500 text-white rounded hover:bg-carbon-600 font-medium text-sm">
          <Upload className="w-4 h-4" />
          Register New Model
        </button>
      </div>

      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Production</h2>
        {productionModel ? (
          <ModelCard model={productionModel} onPromote={(stage) => promoteMutation.mutate({ id: productionModel.id, stage })} />
        ) : (
          <div className="text-slate-500 text-sm">No production model</div>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Staging Candidates</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {stagingModels.map((m) => (
            <ModelCard key={m.id} model={m} onPromote={(stage) => promoteMutation.mutate({ id: m.id, stage })} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Archived & Older</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {archivedModels.map((m) => (
            <ModelCard key={m.id} model={m} onPromote={(stage) => promoteMutation.mutate({ id: m.id, stage })} compact />
          ))}
        </div>
      </section>
    </div>
  );
}

function ModelCard({ model, onPromote, compact }: { model: any; onPromote: (stage: string) => void; compact?: boolean }) {
  return (
    <div className={cn('bg-slate-900 rounded-lg p-4 border border-slate-800', compact ? 'space-y-2' : 'space-y-3')}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-200">{model.name}</h3>
          <p className="text-xs text-slate-500 mt-0.5">v{model.version} • {model.format.toUpperCase()} • {(model.size / 1024 / 1024).toFixed(1)}MB</p>
        </div>
        <span className={cn('text-xs px-2 py-1 rounded-full', stageColors[model.stage as keyof typeof stageColors])}>
          {model.stage}
        </span>
      </div>

      {!compact && (
        <div className="grid grid-cols-4 gap-2 text-center">
          <Metric label="mAP50" value={(model.metrics.mAP50 * 100).toFixed(1)} unit="%" />
          <Metric label="mAP50-95" value={(model.metrics.mAP50_95 * 100).toFixed(1)} unit="%" />
          <Metric label="Precision" value={(model.metrics.precision * 100).toFixed(1)} unit="%" />
          <Metric label="Latency" value={model.metrics.latencyMs.toFixed(1)} unit="ms" />
        </div>
      )}

      <div className="flex gap-2 pt-2">
        {model.stage !== 'Production' && (
          <button
            onClick={() => onPromote('Production')}
            className="flex items-center gap-1 text-xs px-2 py-1 bg-carbon-500/20 text-carbon-400 rounded hover:bg-carbon-500/30"
          >
            <Rocket className="w-3 h-3" />
            Promote
          </button>
        )}
        {model.stage === 'Production' && (
          <button
            onClick={() => onPromote('Archived')}
            className="flex items-center gap-1 text-xs px-2 py-1 bg-slate-700 text-slate-400 rounded hover:bg-slate-600"
          >
            <Archive className="w-3 h-3" />
            Archive
          </button>
        )}
        <button className="flex items-center gap-1 text-xs px-2 py-1 bg-slate-800 text-slate-300 rounded hover:bg-slate-700">
          <GitBranch className="w-3 h-3" />
          Lineage
        </button>
      </div>
    </div>
  );
}

function Metric({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="bg-slate-800 rounded p-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="font-mono font-bold text-slate-200">
        {value}<span className="text-xs text-slate-500">{unit}</span>
      </div>
    </div>
  );
}
