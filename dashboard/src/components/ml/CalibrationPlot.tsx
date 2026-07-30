import { useTheme } from '@/themes/ThemeProvider';
import type { CalibrationData } from '@/ml/types';
import { cn } from '@/lib/utils';

export function CalibrationPlot({ data, height = 350 }: { data: CalibrationData; height?: number }) {
  const { theme } = useTheme();
  const width = 400;
  const padding = 50;
  const innerSize = width - padding * 2;
  
  const xScale = (x: number) => padding + x * innerSize;
  const yScale = (y: number) => padding + (1 - y) * innerSize;
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text">Model Calibration</h3>
        <div className="flex gap-3 text-xs">
          <div className="flex items-center gap-1">
            <span className="text-text-tertiary">ECE:</span>
            <span className={cn(
              'font-mono font-bold',
              data.expectedCalibrationError < 0.05 ? 'text-success' :
              data.expectedCalibrationError < 0.1 ? 'text-warning' : 'text-danger'
            )}>
              {data.expectedCalibrationError.toFixed(3)}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-text-tertiary">MCE:</span>
            <span className="text-text font-mono font-bold">{data.maximumCalibrationError.toFixed(3)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-text-tertiary">Brier:</span>
            <span className="text-text font-mono font-bold">{data.brierScore.toFixed(3)}</span>
          </div>
        </div>
      </div>
      
      <svg width={width} height={height} className="mx-auto">
        {Array.from({ length: 11 }, (_, i) => {
          const v = i / 10;
          return (
            <g key={i}>
              <line x1={xScale(v)} y1={padding} x2={xScale(v)} y2={padding + innerSize} stroke={theme.colors.border} strokeWidth={0.5} />
              <line x1={padding} y1={yScale(v)} x2={padding + innerSize} y2={yScale(v)} stroke={theme.colors.border} strokeWidth={0.5} />
              <text x={xScale(v)} y={padding + innerSize + 15} textAnchor="middle" fontSize={10} fill={theme.colors.textTertiary}>{v.toFixed(1)}</text>
              <text x={padding - 5} y={yScale(v) + 3} textAnchor="end" fontSize={10} fill={theme.colors.textTertiary}>{v.toFixed(1)}</text>
            </g>
          );
        })}
        
        <line x1={xScale(0)} y1={yScale(0)} x2={xScale(1)} y2={yScale(1)} stroke={theme.colors.borderStrong} strokeDasharray="4 4" />
        
        {data.bins.map((bin, i) => {
          const barWidth = innerSize / data.bins.length * 0.8;
          const x = xScale(bin.binCenter) - barWidth / 2;
          const y = yScale(Math.max(bin.actualAccuracy, 0.05));
          const h = padding + innerSize - y;
          return (
            <rect key={i} x={x} y={y} width={barWidth} height={h} 
                  fill={theme.colors.chart2} opacity={0.35} rx={2} />
          );
        })}
        
        <path
          d={data.bins.map((bin, i) => `${i === 0 ? 'M' : 'L'} ${xScale(bin.averageConfidence)} ${yScale(bin.actualAccuracy)}`).join(' ')}
          stroke={theme.colors.primary[500]}
          strokeWidth={2.5}
          fill="none"
        />
        
        {data.bins.map((bin, i) => (
          <circle key={i} cx={xScale(bin.averageConfidence)} cy={yScale(bin.actualAccuracy)} r={4}
                  fill={Math.abs(bin.gap) > 0.1 ? theme.colors.danger[500] : theme.colors.primary[500]} />
        ))}
        
        <text x={width / 2} y={height - 5} textAnchor="middle" fontSize={11} fill={theme.colors.textSecondary}>
          Average Confidence
        </text>
        <text x={-height / 2} y={15} textAnchor="middle" transform="rotate(-90)" fontSize={11} fill={theme.colors.textSecondary}>
          Actual Accuracy
        </text>
      </svg>
    </div>
  );
}
