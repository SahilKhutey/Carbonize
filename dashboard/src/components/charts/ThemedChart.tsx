import { useMemo } from 'react';
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell
} from 'recharts';
import { useTheme } from '@/themes/ThemeProvider';

interface ThemedChartProps {
  type: 'line' | 'area' | 'bar' | 'pie';
  data: any[];
  series: Array<{ key: string; name: string; color?: string; yAxisId?: string }>;
  height?: number;
  xKey?: string;
  title?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  stacked?: boolean;
  formatX?: (value: any) => string;
  formatY?: (value: any) => string;
}

export function ThemedChart({
  type, data, series, height = 300, xKey = 'ts', title,
  showGrid = true, showLegend = true, stacked = false,
  formatX, formatY,
}: ThemedChartProps) {
  const { theme } = useTheme();
  
  const chartColors = useMemo(() => ({
    grid: theme.colors.border,
    text: theme.colors.textTertiary,
    background: theme.colors.surface,
    series: series.map((s, i) => s.color || (theme.colors as any)[`chart${(i % 8) + 1}`]),
  }), [theme, series]);
  
  const tooltipStyle = {
    background: theme.colors.surfaceElevated,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.radius.md,
    color: theme.colors.textPrimary,
    fontSize: '12px',
    boxShadow: theme.shadows.lg,
  };
  
  const renderChart = () => {
    if (type === 'line') {
      return (
        <LineChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />}
          <XAxis
            dataKey={xKey}
            stroke={chartColors.text}
            fontSize={11}
            tickFormatter={formatX}
            tickLine={false}
          />
          <YAxis stroke={chartColors.text} fontSize={11} tickFormatter={formatY} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          {showLegend && <Legend />}
          {series.map((s, i) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.name}
              stroke={chartColors.series[i]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      );
    }
    
    if (type === 'area') {
      return (
        <AreaChart data={data}>
          <defs>
            {series.map((s, i) => (
              <linearGradient key={s.key} id={`grad-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={chartColors.series[i]} stopOpacity={0.6} />
                <stop offset="100%" stopColor={chartColors.series[i]} stopOpacity={0.05} />
              </linearGradient>
            ))}
          </defs>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />}
          <XAxis dataKey={xKey} stroke={chartColors.text} fontSize={11} tickFormatter={formatX} />
          <YAxis stroke={chartColors.text} fontSize={11} tickFormatter={formatY} />
          <Tooltip contentStyle={tooltipStyle} />
          {showLegend && <Legend />}
          {series.map((s, i) => (
            <Area
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.name}
              stroke={chartColors.series[i]}
              fill={`url(#grad-${s.key})`}
              stackId={stacked ? '1' : undefined}
            />
          ))}
        </AreaChart>
      );
    }
    
    if (type === 'bar') {
      return (
        <BarChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />}
          <XAxis dataKey={xKey} stroke={chartColors.text} fontSize={11} tickFormatter={formatX} />
          <YAxis stroke={chartColors.text} fontSize={11} tickFormatter={formatY} />
          <Tooltip contentStyle={tooltipStyle} />
          {showLegend && <Legend />}
          {series.map((s, i) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.name}
              fill={chartColors.series[i]}
              stackId={stacked ? '1' : undefined}
              radius={stacked ? undefined : [4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      );
    }
    
    if (type === 'pie') {
      return (
        <PieChart>
          <Pie
            data={data}
            dataKey={series[0].key}
            nameKey={xKey}
            cx="50%"
            cy="50%"
            outerRadius={100}
            label
          >
            {data.map((_, i) => (
              <Cell key={i} fill={chartColors.series[i % chartColors.series.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          {showLegend && <Legend />}
        </PieChart>
      );
    }
  };
  
  return (
    <div
      className="w-full bg-surface border border-border rounded-theme-md p-3"
      style={{ height: height + (title ? 48 : 16) }}
    >
      {title && <h3 className="text-sm font-semibold text-text mb-2">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        {renderChart() as any}
      </ResponsiveContainer>
    </div>
  );
}
