import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { format } from 'date-fns';

interface TimeSeriesChartProps {
  data: Array<{ ts: number; value: number; label?: string }>;
  height?: number;
  color?: string;
  title?: string;
  unit?: string;
  showArea?: boolean;
  yDomain?: [number | 'auto', number | 'auto'];
}

export function TimeSeriesChart({
  data,
  height = 200,
  color = '#22c55e',
  title,
  unit = '',
  showArea = true,
  yDomain = ['auto', 'auto'],
}: TimeSeriesChartProps) {
  const formattedData = data.map((d) => ({
    ...d,
    time: format(d.ts, 'HH:mm:ss'),
  }));

  const gradientId = `gradient-${color.replace('#', '')}`;

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
      {title && (
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
          {data.length > 0 && (
            <span className="text-2xl font-mono font-bold" style={{ color }}>
              {data[data.length - 1].value.toFixed(1)}
              <span className="text-xs text-slate-500 ml-1">{unit}</span>
            </span>
          )}
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        {showArea ? (
          <AreaChart data={formattedData}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.6} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} interval="preserveStartEnd" />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={yDomain} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2} fill={`url(#${gradientId})`} dot={false} isAnimationActive={false} />
          </AreaChart>
        ) : (
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} interval="preserveStartEnd" />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={yDomain} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
