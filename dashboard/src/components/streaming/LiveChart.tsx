import { useEffect, useRef, useState } from 'react';
import { useTheme } from '@/themes/ThemeProvider';
import { Trash2 } from 'lucide-react';

interface LiveChartProps {
  data: Array<{ ts: number; value: number }>;
  maxPoints?: number;
  height?: number;
  title?: string;
  unit?: string;
  color?: string;
  yMin?: number;
  yMax?: number;
  paused?: boolean;
  onClear?: () => void;
}

export function LiveChart({
  data = [],
  maxPoints = 300,
  height = 220,
  title,
  unit = '',
  color,
  yMin,
  yMax,
  onClear,
}: LiveChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { theme } = useTheme();
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; ts: number } | null>(null);
  
  const lineColor = color || theme.colors.primary[500];
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    
    ctx.clearRect(0, 0, rect.width, rect.height);
    
    if (!data || data.length < 2) return;
    
    const visible = data.slice(-maxPoints);
    const values = visible.map((d) => d.value);
    const minV = yMin ?? Math.min(...values);
    const maxV = yMax ?? Math.max(...values);
    const range = Math.max(maxV - minV, 1e-10);
    
    const tsValues = visible.map((d) => d.ts);
    const tsMin = tsValues[0];
    const tsMax = tsValues[tsValues.length - 1];
    const tsRange = Math.max(tsMax - tsMin, 1);
    
    ctx.strokeStyle = theme.colors.border;
    ctx.lineWidth = 0.5;
    ctx.setLineDash([3, 3]);
    
    for (let i = 0; i <= 4; i++) {
      const y = (i / 4) * (rect.height - 30) + 5;
      ctx.beginPath();
      ctx.moveTo(45, y);
      ctx.lineTo(rect.width - 5, y);
      ctx.stroke();
      
      const value = maxV - (i / 4) * range;
      ctx.fillStyle = theme.colors.textTertiary;
      ctx.font = '10px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(value.toFixed(1), 40, y + 3);
    }
    ctx.setLineDash([]);
    
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    visible.forEach((point, i) => {
      const x = 45 + ((point.ts - tsMin) / tsRange) * (rect.width - 50);
      const y = (rect.height - 30) - ((point.value - minV) / range) * (rect.height - 30) + 5;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    ctx.lineTo(rect.width - 5, rect.height - 25);
    ctx.lineTo(45, rect.height - 25);
    ctx.closePath();
    const gradient = ctx.createLinearGradient(0, 0, 0, rect.height);
    gradient.addColorStop(0, `${lineColor}40`);
    gradient.addColorStop(1, `${lineColor}00`);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    const last = visible[visible.length - 1];
    const lastX = 45 + ((last.ts - tsMin) / tsRange) * (rect.width - 50);
    const lastY = (rect.height - 30) - ((last.value - minV) / range) * (rect.height - 30) + 5;
    
    ctx.fillStyle = lineColor;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fill();
    
    const now = new Date();
    ctx.fillStyle = theme.colors.textTertiary;
    ctx.font = '10px monospace';
    ctx.textAlign = 'right';
    ctx.fillText(now.toLocaleTimeString(), rect.width - 5, rect.height - 8);
  }, [data, maxPoints, lineColor, theme, yMin, yMax]);
  
  const handleMouseMove = (e: React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas || !data || data.length === 0) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (x < 45 || x > rect.width - 5) {
      setHoveredPoint(null);
      return;
    }
    
    const visible = data.slice(-maxPoints);
    const tsValues = visible.map((d) => d.ts);
    const tsMin = tsValues[0];
    const tsMax = tsValues[tsValues.length - 1];
    const tsRange = Math.max(tsMax - tsMin, 1);
    
    const ts = tsMin + ((x - 45) / (rect.width - 50)) * tsRange;
    
    let nearest = visible[0];
    let minDist = Infinity;
    for (const p of visible) {
      const d = Math.abs(p.ts - ts);
      if (d < minDist) {
        minDist = d;
        nearest = p;
      }
    }
    
    setHoveredPoint({ x, y, value: nearest.value, ts: nearest.ts });
  };
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-3">
      {title && (
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-text">{title}</h3>
          <div className="flex items-center gap-2">
            {hoveredPoint && (
              <div className="text-xs font-mono text-text">
                {hoveredPoint.value.toFixed(2)} {unit}
              </div>
            )}
            {onClear && (
              <button onClick={onClear} className="theme-button p-1">
                <Trash2 className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
      )}
      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredPoint(null)}
        className="w-full"
        style={{ height, cursor: 'crosshair' }}
      />
    </div>
  );
}
