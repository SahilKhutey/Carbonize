import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ScanLine, Filter, Download } from 'lucide-react';
import { detectionsApi } from '@/lib/api';
import { formatRelativeTime } from '@/lib/utils';
import { cn } from '@/lib/utils';

export function Detections() {
  const [filter, setFilter] = useState<{ class?: string; minConf?: number }>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: detections = [], isLoading } = useQuery({
    queryKey: ['detections', filter],
    queryFn: () => detectionsApi.list({ limit: 200, ...filter }),
    refetchInterval: 3000,
  });

  const classes = Array.from(new Set(detections.map((d) => d.class)));
  const selected = detections.find((d) => d.id === selectedId);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Detections</h1>
          <p className="text-slate-400 text-sm mt-1">Model inference history with full metadata</p>
        </div>
        <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 text-sm">
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      <div className="bg-slate-900 rounded-lg p-3 border border-slate-800 flex items-center gap-3">
        <Filter className="w-4 h-4 text-slate-500" />
        <select
          onChange={(e) => setFilter({ ...filter, class: e.target.value || undefined })}
          className="bg-slate-800 text-slate-200 text-sm rounded px-2 py-1"
        >
          <option value="">All classes</option>
          {classes.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select
          onChange={(e) => setFilter({ ...filter, minConf: parseFloat(e.target.value) || undefined })}
          className="bg-slate-800 text-slate-200 text-sm rounded px-2 py-1"
        >
          <option value="">Any confidence</option>
          <option value="0.9">≥ 90%</option>
          <option value="0.7">≥ 70%</option>
          <option value="0.5">≥ 50%</option>
        </select>
        <span className="ml-auto text-sm text-slate-500">{detections.length} detections</span>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-7 grid grid-cols-2 gap-3 max-h-[calc(100vh-220px)] overflow-y-auto">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="aspect-video bg-slate-800 animate-pulse rounded-lg" />
            ))
          ) : detections.length === 0 ? (
            <div className="col-span-2 text-center py-12 text-slate-500">
              <ScanLine className="w-12 h-12 mx-auto opacity-30 mb-3" />
              No detections yet
            </div>
          ) : (
            detections.map((det) => (
              <button
                key={det.id}
                onClick={() => setSelectedId(det.id)}
                className={cn(
                  'text-left bg-slate-900 rounded-lg overflow-hidden border transition-colors',
                  selectedId === det.id ? 'border-carbon-500' : 'border-slate-800 hover:border-slate-700'
                )}
              >
                <div className="aspect-video bg-slate-800 relative">
                  <img src={det.imageUrl} alt={det.class} className="w-full h-full object-cover" />
                  <div className="absolute top-2 left-2 bg-black/60 backdrop-blur text-xs text-white px-2 py-1 rounded">
                    {det.class}
                  </div>
                  <div className="absolute bottom-2 right-2 bg-carbon-500 text-xs font-bold px-2 py-1 rounded">
                    {(det.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-2 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>{det.robotId}</span>
                    <span>{formatRelativeTime(det.timestamp)}</span>
                  </div>
                  <div className="text-slate-500 text-[10px] mt-1">v{det.modelVersion}</div>
                </div>
              </button>
            ))
          )}
        </div>

        <div className="col-span-5 bg-slate-900 rounded-lg border border-slate-800 p-4 max-h-[calc(100vh-220px)] overflow-y-auto">
          {selected ? (
            <div className="space-y-4">
              <div className="aspect-video bg-slate-800 rounded overflow-hidden">
                <img src={selected.imageUrl} alt={selected.class} className="w-full h-full object-contain" />
              </div>
              <h3 className="font-semibold text-slate-200">{selected.class}</h3>
              <div className="space-y-1 text-sm">
                <Row label="ID" value={selected.id} />
                <Row label="Timestamp" value={new Date(selected.timestamp).toLocaleString()} />
                <Row label="Robot" value={selected.robotId} />
                <Row label="Confidence" value={`${(selected.confidence * 100).toFixed(2)}%`} />
                <Row label="Model" value={selected.modelVersion} />
                <Row label="BBox" value={selected.bbox.map((n) => n.toFixed(0)).join(', ')} />
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-12">
              <ScanLine className="w-12 h-12 mx-auto opacity-30 mb-3" />
              Click a detection to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}:</span>
      <span className="text-slate-200 font-mono text-xs">{value}</span>
    </div>
  );
}
