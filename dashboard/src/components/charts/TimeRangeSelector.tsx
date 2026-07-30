import React, { useState, useRef } from 'react';
import { Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

export type TimeRange =
  | '5m' | '15m' | '1h' | '6h' | '24h' | '7d' | '30d' | 'custom';

export interface TimeRangeValue {
  start: number;
  end: number;
  label: string;
}

interface TimeRangeSelectorProps {
  value: TimeRangeValue;
  onChange: (range: TimeRangeValue) => void;
  presets?: TimeRange[];
  minDate?: Date;
  maxDate?: Date;
  showComparison?: boolean;
  onComparisonChange?: (enabled: boolean) => void;
}

const DEFAULT_PRESETS: TimeRange[] = ['5m', '15m', '1h', '6h', '24h', '7d', '30d', 'custom'];

const PRESET_LABELS: Record<TimeRange, string> = {
  '5m': 'Last 5 min',
  '15m': 'Last 15 min',
  '1h': 'Last hour',
  '6h': 'Last 6 hours',
  '24h': 'Last 24 hours',
  '7d': 'Last 7 days',
  '30d': 'Last 30 days',
  'custom': 'Custom range',
};

export function TimeRangeSelector({
  value,
  onChange,
  presets = DEFAULT_PRESETS,
  minDate,
  maxDate,
  showComparison = true,
  onComparisonChange,
}: TimeRangeSelectorProps) {
  const [showCustom, setShowCustom] = useState(false);
  const [activePreset, setActivePreset] = useState<TimeRange>(detectPreset(value));
  const [comparisonEnabled, setComparisonEnabled] = useState(false);
  
  function detectPreset(v: TimeRangeValue): TimeRange {
    const duration = v.end - v.start;
    const m = 60_000, h = 3_600_000, d = 86_400_000;
    if (duration <= 5 * m) return '5m';
    if (duration <= 15 * m) return '15m';
    if (duration <= h) return '1h';
    if (duration <= 6 * h) return '6h';
    if (duration <= 24 * h) return '24h';
    if (duration <= 7 * d) return '7d';
    if (duration <= 30 * d) return '30d';
    return 'custom';
  }
  
  const selectPreset = (preset: TimeRange) => {
    setActivePreset(preset);
    if (preset === 'custom') {
      setShowCustom(true);
      return;
    }
    setShowCustom(false);
    const now = Date.now();
    const duration = computeDuration(preset);
    onChange({
      start: now - duration,
      end: now,
      label: PRESET_LABELS[preset],
    });
  };
  
  const applyCustom = (start: Date, end: Date) => {
    onChange({
      start: start.getTime(),
      end: end.getTime(),
      label: `${start.toLocaleString()} - ${end.toLocaleString()}`,
    });
    setShowCustom(false);
  };
  
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className="flex items-center gap-1 bg-surface border border-border rounded-theme-md p-1">
        <Clock className="w-4 h-4 text-text-tertiary ml-2" />
        {presets.map((preset) => (
          <button
            key={preset}
            onClick={() => selectPreset(preset)}
            className={cn(
              'px-3 py-1 text-xs rounded transition-colors',
              activePreset === preset
                ? 'bg-primary-500 text-white font-medium'
                : 'text-text-secondary hover:text-text hover:bg-surface-hover'
            )}
          >
            {preset === 'custom' ? 'Custom' : preset}
          </button>
        ))}
      </div>
      
      {showComparison && (
        <label className="flex items-center gap-2 theme-button cursor-pointer text-xs font-medium">
          <input
            type="checkbox"
            checked={comparisonEnabled}
            onChange={(e) => {
              setComparisonEnabled(e.target.checked);
              onComparisonChange?.(e.target.checked);
            }}
            className="accent-primary-500"
          />
          <span>Compare to previous</span>
        </label>
      )}
      
      <div className="text-xs text-text-tertiary font-mono ml-auto">
        {value.label}
      </div>
      
      {showCustom && (
        <CustomRangeModal
          onApply={applyCustom}
          onClose={() => setShowCustom(false)}
          minDate={minDate}
          maxDate={maxDate}
          initialStart={new Date(value.start)}
          initialEnd={new Date(value.end)}
        />
      )}
    </div>
  );
}

function computeDuration(preset: TimeRange): number {
  const m = 60_000, h = 3_600_000, d = 86_400_000;
  switch (preset) {
    case '5m': return 5 * m;
    case '15m': return 15 * m;
    case '1h': return h;
    case '6h': return 6 * h;
    case '24h': return 24 * h;
    case '7d': return 7 * d;
    case '30d': return 30 * d;
    default: return 3600_000;
  }
}

function CustomRangeModal({ onApply, onClose, initialStart, initialEnd }: any) {
  const [startInput, setStartInput] = useState(initialStart.toISOString().slice(0, 16));
  const [endInput, setEndInput] = useState(initialEnd.toISOString().slice(0, 16));
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated border border-border rounded-theme-lg p-6 w-96 shadow-theme-xl">
        <h3 className="font-semibold text-text mb-4">Custom Time Range</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-text-tertiary mb-1 block">Start Time</label>
            <input
              type="datetime-local"
              value={startInput}
              onChange={(e) => setStartInput(e.target.value)}
              className="w-full bg-surface border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono outline-none focus:border-primary-500"
            />
          </div>
          <div>
            <label className="text-xs text-text-tertiary mb-1 block">End Time</label>
            <input
              type="datetime-local"
              value={endInput}
              onChange={(e) => setEndInput(e.target.value)}
              className="w-full bg-surface border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono outline-none focus:border-primary-500"
            />
          </div>
          <div className="flex gap-2 justify-end mt-4 pt-2 border-t border-border">
            <button onClick={onClose} className="theme-button text-xs">Cancel</button>
            <button
              onClick={() => onApply(new Date(startInput), new Date(endInput))}
              className="theme-button-primary text-xs font-semibold"
            >
              Apply Range
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function DragRangeSelector({ value, onChange, data }: any) {
  const ref = useRef<HTMLDivElement>(null);
  const [dragStart, setDragStart] = useState<number | null>(null);
  const [dragEnd, setDragEnd] = useState<number | null>(null);
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = (x / rect.width) * (value.end - value.start) + value.start;
    setDragStart(t);
    setDragEnd(t);
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragStart === null || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = (x / rect.width) * (value.end - value.start) + value.start;
    setDragEnd(t);
  };
  
  const handleMouseUp = () => {
    if (dragStart !== null && dragEnd !== null) {
      const start = Math.min(dragStart, dragEnd);
      const end = Math.max(dragStart, dragEnd);
      onChange({ start, end, label: `${new Date(start).toLocaleTimeString()} - ${new Date(end).toLocaleTimeString()}` });
    }
    setDragStart(null);
    setDragEnd(null);
  };
  
  const startPct = dragStart ? ((dragStart - value.start) / (value.end - value.start)) * 100 : null;
  const endPct = dragEnd ? ((dragEnd - value.start) / (value.end - value.start)) * 100 : null;
  const left = startPct !== null && endPct !== null ? Math.min(startPct, endPct) : 0;
  const width = startPct !== null && endPct !== null ? Math.abs(endPct - startPct) : 0;
  
  return (
    <div
      ref={ref}
      className="h-12 bg-surface-elevated border border-border rounded-theme-md cursor-crosshair relative overflow-hidden"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <svg className="absolute inset-0 w-full h-full opacity-30">
        <polyline
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          points={data.map((d: any, i: number) => `${(i / (data.length || 1)) * 100}%,${100 - (d.value / Math.max(...data.map((x: any) => x.value), 1)) * 100}%`).join(' ')}
        />
      </svg>
      
      {startPct !== null && endPct !== null && (
        <div
          className="absolute top-0 bottom-0 bg-primary-500/20 border-x-2 border-primary-500"
          style={{ left: `${left}%`, width: `${width}%` }}
        />
      )}
    </div>
  );
}
