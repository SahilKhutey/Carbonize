import { useMemo } from 'react';

interface HeatmapGridProps {
  data: number[][];
  cellSize?: number;
  labels?: { x: string[]; y: string[] };
  maxValue?: number;
}

export function HeatmapGrid({ data, cellSize = 30, labels, maxValue }: HeatmapGridProps) {
  const max = useMemo(() => maxValue ?? Math.max(...data.flat(), 1), [data, maxValue]);

  const colorScale = (v: number) => {
    const t = v / max;
    if (t < 0.2) return 'bg-slate-800';
    if (t < 0.4) return 'bg-carbon-900';
    if (t < 0.6) return 'bg-carbon-700';
    if (t < 0.8) return 'bg-carbon-500';
    return 'bg-carbon-300';
  };

  return (
    <div className="inline-block">
      <div className="flex">
        {labels?.y && <div className="w-20" />}
        {labels?.x.map((label, i) => (
          <div key={i} className="text-xs text-slate-500 text-center" style={{ width: cellSize }}>
            {label}
          </div>
        ))}
      </div>
      {data.map((row, ri) => (
        <div key={ri} className="flex items-center">
          {labels?.y && (
            <div className="w-20 text-xs text-slate-500 pr-2 text-right">{labels.y[ri]}</div>
          )}
          {row.map((value, ci) => (
            <div
              key={ci}
              className={`${colorScale(value)} border border-slate-900 flex items-center justify-center text-xs text-white/60`}
              style={{ width: cellSize, height: cellSize }}
              title={`${value.toFixed(0)}`}
            >
              {value > 0 ? value.toFixed(0) : ''}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
