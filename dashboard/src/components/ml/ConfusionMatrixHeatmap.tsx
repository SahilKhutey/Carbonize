import { useState } from 'react';
import { cn } from '@/lib/utils';

interface ConfusionMatrixProps {
  classes: string[];
  matrix: number[][];
  normalized: number[][];
  onCellClick?: (i: number, j: number) => void;
}

export function ConfusionMatrixHeatmap({ classes, matrix, normalized, onCellClick }: ConfusionMatrixProps) {
  const [normalized2, setNormalized] = useState(true);
  const [hovered, setHovered] = useState<{ i: number; j: number } | null>(null);
  
  const data = normalized2 ? normalized : matrix;
  const max = Math.max(...data.flat());
  
  const getColor = (value: number) => {
    const t = value / max;
    if (t < 0.1) return 'bg-surface-elevated';
    if (t < 0.3) return 'bg-primary-500/20';
    if (t < 0.5) return 'bg-primary-500/40';
    if (t < 0.7) return 'bg-primary-500/60';
    if (t < 0.9) return 'bg-primary-500/80';
    return 'bg-primary-500';
  };
  
  const getTextColor = (value: number) => {
    const t = value / max;
    return t > 0.5 ? 'text-white' : 'text-text';
  };
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">Confusion Matrix</h3>
        <div className="flex gap-1 bg-surface-elevated rounded-theme-md p-1 border border-border">
          <button
            onClick={() => setNormalized(true)}
            className={cn('px-2 py-1 text-xs rounded', normalized2 ? 'bg-primary-500 text-white font-medium' : 'text-text-secondary')}
          >
            Normalized
          </button>
          <button
            onClick={() => setNormalized(false)}
            className={cn('px-2 py-1 text-xs rounded', !normalized2 ? 'bg-primary-500 text-white font-medium' : 'text-text-secondary')}
          >
            Counts
          </button>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="p-1"></th>
              <th colSpan={classes.length} className="text-center text-xs text-text-tertiary p-1 font-medium">Predicted Class</th>
            </tr>
            <tr>
              <th className="p-1"></th>
              {classes.map((c) => (
                <th key={c} className="p-1 text-xs text-text-secondary font-normal" style={{ minWidth: 60 }}>
                  <div className="transform -rotate-45 origin-center whitespace-nowrap">{c}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {classes.map((actual, i) => (
              <tr key={actual}>
                <td className="text-xs text-text-secondary text-right pr-2 py-1">{actual}</td>
                {classes.map((_, j) => {
                  const value = data[i][j];
                  const isDiagonal = i === j;
                  const isHovered = hovered?.i === i && hovered?.j === j;
                  return (
                    <td
                      key={j}
                      className={cn(
                        'p-1 text-center text-xs font-mono cursor-pointer transition-all border border-border-muted',
                        getColor(value),
                        getTextColor(value),
                        isHovered && 'ring-2 ring-primary-500',
                        isDiagonal && 'font-bold',
                      )}
                      onMouseEnter={() => setHovered({ i, j })}
                      onMouseLeave={() => setHovered(null)}
                      onClick={() => onCellClick?.(i, j)}
                    >
                      {normalized2 ? (value * 100).toFixed(0) : value}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {hovered && (
        <div className="mt-3 text-xs text-text-secondary">
          <span className="font-mono">
            Actual: <span className="text-text font-semibold">{classes[hovered.i]}</span>
            {' → '}
            Predicted: <span className="text-text font-semibold">{classes[hovered.j]}</span>
          </span>
          <span className="ml-4 font-mono">
            {normalized2 ? `${(data[hovered.i][hovered.j] * 100).toFixed(2)}%` : `${data[hovered.i][hovered.j]} samples`}
          </span>
        </div>
      )}
    </div>
  );
}
