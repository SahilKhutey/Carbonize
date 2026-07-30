import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: number;
  icon?: React.ReactNode;
  color?: 'carbon' | 'sky' | 'warning' | 'critical' | 'neutral';
  loading?: boolean;
}

const colorMap = {
  carbon: 'text-carbon-400 bg-carbon-500/10 border-carbon-500/30',
  sky: 'text-sky-400 bg-sky-500/10 border-sky-500/30',
  warning: 'text-warning-400 bg-warning-500/10 border-warning-500/30',
  critical: 'text-critical-400 bg-critical-500/10 border-critical-500/30',
  neutral: 'text-slate-300 bg-slate-800 border-slate-700',
};

export function StatCard({ label, value, unit, trend, icon, color = 'carbon', loading }: StatCardProps) {
  const TrendIcon = trend === undefined ? null : trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendColor = trend === undefined ? '' : trend > 0 ? 'text-carbon-400' : trend < 0 ? 'text-critical-400' : 'text-slate-500';

  return (
    <div className={cn('bg-slate-900 rounded-lg p-4 border', colorMap[color])}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs text-slate-400 uppercase tracking-wide">{label}</p>
          {loading ? (
            <div className="h-8 w-20 bg-slate-800 animate-pulse rounded mt-1" />
          ) : (
            <div className="flex items-baseline gap-1 mt-1">
              <p className="text-2xl font-bold font-mono">{value}</p>
              {unit && <span className="text-sm text-slate-500">{unit}</span>}
            </div>
          )}
          {trend !== undefined && TrendIcon && (
            <div className={cn('flex items-center gap-1 text-xs mt-1', trendColor)}>
              <TrendIcon className="w-3 h-3" />
              <span>{Math.abs(trend).toFixed(1)}%</span>
            </div>
          )}
        </div>
        {icon && <div className="opacity-60">{icon}</div>}
      </div>
    </div>
  );
}
