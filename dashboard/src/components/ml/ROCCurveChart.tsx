import React, { useRef, useState } from 'react';
import { useTheme } from '@/themes/ThemeProvider';
import { cn } from '@/lib/utils';
import type { CurveData } from '@/ml/types';

interface ROCCurveChartProps {
  curves: Array<{ className: string; data: CurveData; color?: string }>;
  height?: number;
  type?: 'roc' | 'pr';
}

export function ROCCurveChart({ curves, height = 360, type = 'roc' }: ROCCurveChartProps) {
  const { theme } = useTheme();
  const [hovered, setHovered] = useState<{ x: number; y: number; className: string; threshold: number } | null>(null);
  const [selectedClass, setSelectedClass] = useState<string>(curves[0]?.className || '');
  const svgRef = useRef<SVGSVGElement>(null);
  
  const width = 450;
  const padding = 50;
  const innerWidth = width - padding * 2;
  const innerHeight = height - padding * 2;
  
  const xScale = (x: number) => padding + x * innerWidth;
  const yScale = (y: number) => padding + (1 - y) * innerHeight;
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width * width;
    const y = (e.clientY - rect.top) / rect.height * height;
    const dataX = (x - padding) / innerWidth;
    const dataY = 1 - (y - padding) / innerHeight;
    
    if (dataX >= 0 && dataX <= 1 && dataY >= 0 && dataY <= 1) {
      const curve = curves.find((c) => c.className === selectedClass);
      if (curve) {
        let nearest = curve.data.points[0];
        let minDist = Infinity;
        for (const p of curve.data.points) {
          const d = Math.hypot(p.x - dataX, p.y - dataY);
          if (d < minDist) {
            minDist = d;
            nearest = p;
          }
        }
        setHovered({
          x: dataX,
          y: nearest.y,
          className: selectedClass,
          threshold: nearest.threshold || 0,
        });
      }
    }
  };
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">
          {type === 'roc' ? 'ROC Curve' : 'Precision-Recall Curve'}
        </h3>
        <select
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
          className="bg-surface-elevated text-text text-xs rounded-theme-md px-2 py-1 border border-border"
        >
          {curves.map((c) => (
            <option key={c.className} value={c.className}>{c.className}</option>
          ))}
        </select>
      </div>
      
      <div className="flex flex-col md:flex-row items-center gap-4">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          className="flex-shrink-0"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHovered(null)}
        >
          {Array.from({ length: 11 }, (_, i) => {
            const v = i / 10;
            return (
              <g key={i}>
                <line x1={xScale(v)} y1={padding} x2={xScale(v)} y2={padding + innerHeight} stroke={theme.colors.border} strokeWidth={0.5} />
                <line x1={padding} y1={yScale(v)} x2={padding + innerWidth} y2={yScale(v)} stroke={theme.colors.border} strokeWidth={0.5} />
                <text x={xScale(v)} y={padding + innerHeight + 15} textAnchor="middle" fontSize={10} fill={theme.colors.textTertiary}>
                  {v.toFixed(1)}
                </text>
                <text x={padding - 5} y={yScale(v) + 3} textAnchor="end" fontSize={10} fill={theme.colors.textTertiary}>
                  {v.toFixed(1)}
                </text>
              </g>
            );
          })}
          
          <line
            x1={xScale(0)} y1={yScale(0)}
            x2={xScale(1)} y2={yScale(1)}
            stroke={theme.colors.borderStrong}
            strokeDasharray="4 4"
          />
          
          {curves.map((curve, i) => {
            const color = curve.color || (theme.colors as any)[`chart${(i % 8) + 1}`];
            const path = curve.data.points
              .map((p, j) => `${j === 0 ? 'M' : 'L'} ${xScale(p.x)} ${yScale(p.y)}`)
              .join(' ');
            return (
              <g key={curve.className}>
                <path
                  d={path}
                  stroke={color}
                  strokeWidth={curve.className === selectedClass ? 3 : 1.5}
                  fill="none"
                  opacity={curve.className === selectedClass ? 1 : 0.3}
                />
              </g>
            );
          })}
          
          {hovered && (
            <g>
              <line x1={xScale(hovered.x)} y1={padding} x2={xScale(hovered.x)} y2={padding + innerHeight} stroke={theme.colors.primary[500]} strokeDasharray="2 2" />
              <line x1={padding} y1={yScale(hovered.y)} x2={padding + innerWidth} y2={yScale(hovered.y)} stroke={theme.colors.primary[500]} strokeDasharray="2 2" />
              <circle cx={xScale(hovered.x)} cy={yScale(hovered.y)} r={4} fill={theme.colors.primary[500]} />
            </g>
          )}
          
          <text x={width / 2} y={height - 5} textAnchor="middle" fontSize={11} fill={theme.colors.textSecondary}>
            {type === 'roc' ? 'False Positive Rate' : 'Recall'}
          </text>
          <text x={-height / 2} y={15} textAnchor="middle" transform="rotate(-90)" fontSize={11} fill={theme.colors.textSecondary}>
            {type === 'roc' ? 'True Positive Rate' : 'Precision'}
          </text>
        </svg>
        
        <div className="w-full md:w-48 space-y-2">
          {curves.map((c, i) => (
            <div
              key={c.className}
              onClick={() => setSelectedClass(c.className)}
              className={cn(
                'p-2 rounded-theme-md cursor-pointer transition-colors border',
                selectedClass === c.className ? 'bg-surface-elevated border-primary-500/40' : 'border-transparent hover:bg-surface-hover'
              )}
            >
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded" style={{ background: c.color || (theme.colors as any)[`chart${(i % 8) + 1}`] }} />
                <div className="text-xs text-text font-mono font-medium">{c.className}</div>
              </div>
              <div className="ml-5 text-[11px] text-text-tertiary">
                AUC: <span className="text-text font-mono font-semibold">{c.data.auc.toFixed(3)}</span>
              </div>
            </div>
          ))}
          
          {hovered && (
            <div className="mt-4 p-3 bg-surface-elevated border border-border rounded-theme-md text-xs">
              <div className="text-text-tertiary">At threshold</div>
              <div className="text-lg font-bold text-text font-mono">{hovered.threshold.toFixed(3)}</div>
              <div className="mt-1 space-y-0.5 text-text-secondary font-mono">
                <div>X: {hovered.x.toFixed(3)}</div>
                <div>Y: {hovered.y.toFixed(3)}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
