import { useEffect, useRef, useState } from 'react';
import { Activity, AlertTriangle, Zap, TrendingUp } from 'lucide-react';

interface EventStreamProps {
  events: any[];
  maxEvents?: number;
  height?: number;
  eventTypes?: string[];
}

export function EventStream({ events = [], maxEvents = 500, height = 400, eventTypes }: EventStreamProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events, autoScroll]);
  
  const visible = events
    .filter((e) => !eventTypes || eventTypes.includes(e.type))
    .slice(-maxEvents);
  
  const getIcon = (event: any) => {
    switch (event.type) {
      case 'telemetry': return <Activity className="w-4 h-4 text-sky-400" />;
      case 'detection': return <Zap className="w-4 h-4 text-primary-500" />;
      case 'alert': 
        const sev = event.data?.severity;
        return <AlertTriangle className={`w-4 h-4 ${sev === 'critical' ? 'text-danger' : sev === 'warning' ? 'text-warning' : 'text-info'}`} />;
      case 'anomaly': return <TrendingUp className="w-4 h-4 text-warning" />;
      default: return <Activity className="w-4 h-4 text-text-tertiary" />;
    }
  };
  
  const formatEvent = (event: any) => {
    const data = event.data || {};
    switch (event.type) {
      case 'telemetry':
        return `${data.metric_type || 'value'}: ${data.value?.toFixed(2)} ${data.unit || ''} (${data.robot_id || 'sys'})`;
      case 'detection':
        return `${data.class_name || 'object'} detected (${((data.confidence || 0.9) * 100).toFixed(0)}%) by ${data.robot_id || 'sys'}`;
      case 'alert':
        return data.message || data.alert_type || 'System Alert';
      case 'anomaly':
        return `Anomaly in ${data.key || 'metric'}: z=${data.z_score?.toFixed(2) || '3.2'}`;
      default:
        return JSON.stringify(data).slice(0, 100);
    }
  };
  
  return (
    <div className="bg-surface border border-border rounded-theme-md p-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-text">Live Event Stream</h3>
        <label className="flex items-center gap-2 text-xs text-text-secondary">
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
            className="accent-primary-500"
          />
          Auto-scroll
        </label>
      </div>
      
      <div
        ref={containerRef}
        className="overflow-y-auto space-y-1 font-mono text-xs"
        style={{ height }}
      >
        {visible.length === 0 ? (
          <div className="text-text-tertiary text-center py-8">Waiting for events...</div>
        ) : (
          visible.map((event, i) => (
            <div
              key={i}
              className="flex items-start gap-2 p-2 rounded-theme-md hover:bg-surface-elevated transition-colors border-b border-border/20"
            >
              {getIcon(event)}
              <div className="flex-1 min-w-0">
                <div className="text-text-tertiary text-[10px]">
                  {new Date(event.timestamp || Date.now()).toLocaleTimeString()}
                </div>
                <div className="text-text truncate mt-0.5">{formatEvent(event)}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
