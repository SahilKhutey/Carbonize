import React, { useRef, useEffect, useState, useMemo } from 'react';
import { useTheme } from '@/themes/ThemeProvider';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

export interface HeatmapCell {
  row: number;
  col: number;
  value: number;
  metadata?: Record<string, any>;
}

interface InteractiveHeatmapProps {
  data: HeatmapCell[][];
  rowLabels?: string[];
  colLabels?: string[];
  cellSize?: number;
  valueFormatter?: (value: number) => string;
  onCellClick?: (cell: HeatmapCell) => void;
  onCellHover?: (cell: HeatmapCell | null) => void;
  showTooltip?: boolean;
  title?: string;
  unit?: string;
  colorScale?: 'thermal' | 'viridis' | 'cool' | 'diverging';
}

const COLOR_SCALES = {
  thermal: [
    '#0f172a', '#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb',
    '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe',
    '#fef3c7', '#fde68a', '#fcd34d', '#fbbf24', '#f59e0b',
    '#d97706', '#b45309', '#92400e', '#78350f',
  ],
  viridis: [
    '#440154', '#482878', '#3e4989', '#31688e', '#26828e',
    '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
  ],
  cool: [
    '#00ffff', '#1fe5e5', '#3fcccd', '#5eb3b5', '#7e999c',
    '#9d8084', '#bd666b', '#dc4c53', '#fc333a', '#ff1a22',
  ],
  diverging: [
    '#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0',
    '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f',
  ],
};

export function InteractiveHeatmap({
  data,
  rowLabels,
  colLabels,
  cellSize = 28,
  valueFormatter = (v) => v.toFixed(1),
  onCellClick,
  onCellHover,
  showTooltip = true,
  title,
  unit = '',
  colorScale = 'thermal',
}: InteractiveHeatmapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const { theme } = useTheme();
  
  const { minValue, maxValue } = useMemo(() => {
    const flat = data.flat();
    const values = flat.map((c) => c.value);
    return {
      minValue: Math.min(...values),
      maxValue: Math.max(...values),
    };
  }, [data]);
  
  const getColor = (value: number) => {
    const scale = COLOR_SCALES[colorScale];
    const t = (value - minValue) / (maxValue - minValue || 1);
    const idx = Math.floor(t * (scale.length - 1));
    return scale[Math.max(0, Math.min(scale.length - 1, idx))];
  };
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const rows = data.length;
    const cols = data[0]?.length || 0;
    const dpr = window.devicePixelRatio || 1;
    
    const labelWidth = rowLabels ? 80 : 0;
    const labelHeight = colLabels ? 30 : 0;
    const width = cols * cellSize + labelWidth;
    const height = rows * cellSize + labelHeight;
    
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);
    
    ctx.fillStyle = theme.colors.surface;
    ctx.fillRect(0, 0, width, height);
    
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cell = data[r][c];
        if (!cell) continue;
        
        const x = c * cellSize + labelWidth;
        const y = r * cellSize + labelHeight;
        
        ctx.fillStyle = getColor(cell.value);
        ctx.fillRect(x, y, cellSize - 1, cellSize - 1);
        
        if (cellSize > 20) {
          ctx.fillStyle = getContrastColor(getColor(cell.value));
          ctx.font = '10px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(valueFormatter(cell.value), x + cellSize / 2, y + cellSize / 2);
        }
      }
    }
    
    if (rowLabels) {
      ctx.fillStyle = theme.colors.textSecondary;
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      for (let r = 0; r < rows; r++) {
        ctx.fillText(rowLabels[r] || '', labelWidth - 5, r * cellSize + cellSize / 2 + labelHeight);
      }
    }
    
    if (colLabels) {
      ctx.fillStyle = theme.colors.textSecondary;
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'bottom';
      for (let c = 0; c < cols; c++) {
        ctx.save();
        ctx.translate(c * cellSize + cellSize / 2 + labelWidth, labelHeight - 5);
        ctx.rotate(-Math.PI / 4);
        ctx.fillText(colLabels[c] || '', 0, 0);
        ctx.restore();
      }
    }
  }, [data, rowLabels, colLabels, cellSize, theme, minValue, maxValue, valueFormatter]);
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
      return;
    }
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePos({ x: e.clientX, y: e.clientY });
    
    const labelWidth = rowLabels ? 80 : 0;
    const labelHeight = colLabels ? 30 : 0;
    const col = Math.floor((x - labelWidth) / cellSize);
    const row = Math.floor((y - labelHeight) / cellSize);
    
    if (row >= 0 && row < data.length && col >= 0 && col < (data[0]?.length || 0)) {
      const cell = data[row][col];
      if (cell) {
        setHoveredCell(cell);
        onCellHover?.(cell);
      }
    } else {
      setHoveredCell(null);
      onCellHover?.(null);
    }
  };
  
  const handleMouseLeave = () => {
    setHoveredCell(null);
    onCellHover?.(null);
  };
  
  const handleClick = () => {
    if (!hoveredCell) return;
    onCellClick?.(hoveredCell);
  };
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-4">
      {title && (
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-text">{title}</h3>
          <div className="flex items-center gap-2">
            <button onClick={() => setZoom((z) => Math.min(3, z * 1.2))} className="theme-button p-1">
              <ZoomIn className="w-4 h-4" />
            </button>
            <button onClick={() => setZoom((z) => Math.max(0.5, z / 1.2))} className="theme-button p-1">
              <ZoomOut className="w-4 h-4" />
            </button>
            <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} className="theme-button p-1">
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
      
      <div
        ref={containerRef}
        className="relative overflow-auto"
        style={{ maxHeight: 500 }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onMouseDown={(e) => { setIsDragging(true); setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y }); }}
        onMouseUp={() => setIsDragging(false)}
      >
        <canvas
          ref={canvasRef}
          style={{
            transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
            transformOrigin: 'top left',
            imageRendering: 'pixelated',
          }}
        />
      </div>
      
      {showTooltip && hoveredCell && (
        <div
          className="fixed pointer-events-none bg-surface-elevated border border-border rounded-theme-md px-2 py-1 text-xs text-text shadow-theme-lg z-50"
          style={{
            left: mousePos.x + 10,
            top: mousePos.y + 10,
          }}
        >
          <div className="font-mono">
            {valueFormatter(hoveredCell.value)}{unit && <span className="text-text-tertiary ml-1">{unit}</span>}
          </div>
          {hoveredCell.metadata && (
            <div className="text-text-tertiary text-[10px] mt-0.5">
              {Object.entries(hoveredCell.metadata).slice(0, 2).map(([k, v]) => (
                <div key={k}>{k}: {String(v)}</div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <div className="flex items-center gap-3 mt-3">
        <span className="text-xs text-text-tertiary">{valueFormatter(minValue)}</span>
        <div className="flex-1 h-2 rounded-full" style={{ background: `linear-gradient(to right, ${COLOR_SCALES[colorScale].join(', ')})` }} />
        <span className="text-xs text-text-tertiary">{valueFormatter(maxValue)}</span>
      </div>
    </div>
  );
}

function getContrastColor(hex: string): string {
  if (!hex || hex.length < 7) return '#ffffff';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#ffffff';
}
