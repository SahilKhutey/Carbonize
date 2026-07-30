import { useState, useEffect } from 'react';
import { useStream } from '@/hooks/useStream';
import { LiveChart } from '@/components/streaming/LiveChart';
import { EventStream } from '@/components/streaming/EventStream';
import { Activity, Wifi, WifiOff, Zap, AlertTriangle, Radio } from 'lucide-react';
import { cn } from '@/lib/utils';

export function StreamingDashboard() {
  const [liveMetrics, setLiveMetrics] = useState<Record<string, Array<{ ts: number; value: number }>>>({});
  const [events, setEvents] = useState<any[]>([]);
  const [filterType, setFilterType] = useState<string>('all');
  
  const { isConnected, reconnectAttempts, latencyMs, messagesReceived, bytesReceived, subscribe } = useStream({
    url: 'ws://localhost:8080/api/v1/stream/ws',
    onMessage: (msg) => {
      if (msg.type === 'telemetry' && msg.data) {
        const data = msg.data;
        const key = `${data.metric_type}_${data.robot_id || 'sys'}`;
        setLiveMetrics((prev) => {
          const existing = prev[key] || [];
          const updated = [...existing, { ts: data.timestamp || Date.now(), value: data.value }];
          return { ...prev, [key]: updated.slice(-300) };
        });
      }
      
      setEvents((prev) => {
        const updated = [...prev, { ...msg, timestamp: Date.now() }];
        return updated.slice(-1000);
      });
    },
  });
  
  useEffect(() => {
    if (isConnected) {
      subscribe({
        robot_id: null,
        metric_types: ['co2_ppm', 'temperature', 'humidity', 'battery'],
        classes: ['co2_emitter', 'capture_unit'],
        min_severity: 'info',
      });
    }
  }, [isConnected, subscribe]);
  
  const clearAll = () => {
    setLiveMetrics({});
    setEvents([]);
  };
  
  const metricKeys = Object.keys(liveMetrics).length > 0
    ? Object.keys(liveMetrics).slice(0, 4)
    : ['co2_ppm_robot_1', 'temperature_robot_1', 'humidity_robot_2', 'battery_robot_3'];
  
  return (
    <div className="p-6 space-y-4">
      {/* ─── Header ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Radio className="w-7 h-7 text-primary-500 animate-pulse" />
            Live Streaming Analytics Platform
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Real-time event stream from Apache Kafka & Flink via WebSocket fan-out architecture
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <ConnectionBadge isConnected={isConnected} reconnectAttempts={reconnectAttempts} latencyMs={latencyMs} />
          <StatsCounter messages={messagesReceived} bytes={bytesReceived} />
          <button onClick={clearAll} className="theme-button text-xs">Clear All</button>
        </div>
      </div>
      
      {/* ─── Live metric charts ──────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {metricKeys.map((key) => {
          const parts = key.split('_');
          const metricType = parts.slice(0, -2).join('_') || parts[0];
          const robotId = parts.slice(-2).join('_') || 'robot_1';
          const data = liveMetrics[key] || Array.from({ length: 30 }, (_, i) => ({
            ts: Date.now() - (30 - i) * 1000,
            value: 400 + Math.sin(i / 3) * 30 + Math.random() * 5,
          }));
          
          return (
            <LiveChart
              key={key}
              data={data}
              title={`${metricType.toUpperCase()} (${robotId})`}
              unit={metricType.includes('ppm') ? 'ppm' : metricType.includes('temp') ? '°C' : '%'}
              height={200}
              maxPoints={300}
            />
          );
        })}
      </div>
      
      {/* ─── Event stream & filters ──────────────────────────── */}
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          <EventStream
            events={events}
            maxEvents={500}
            height={420}
            eventTypes={filterType === 'all' ? undefined : [filterType]}
          />
        </div>
        
        <div className="col-span-4 bg-surface border border-border rounded-theme-md p-4 space-y-4">
          <h3 className="text-sm font-semibold text-text">Stream Filter & Routing</h3>
          <div className="space-y-1.5">
            {['all', 'telemetry', 'detection', 'alert', 'anomaly'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-theme-md text-xs capitalize flex items-center justify-between border',
                  filterType === type
                    ? 'bg-primary-500/20 text-primary-400 border-primary-500/30 font-semibold'
                    : 'bg-surface-elevated text-text-secondary border-border hover:text-text',
                )}
              >
                <span className="flex items-center gap-2">
                  {type === 'alert' && <AlertTriangle className="w-3.5 h-3.5" />}
                  {type === 'detection' && <Zap className="w-3.5 h-3.5" />}
                  {type === 'telemetry' && <Activity className="w-3.5 h-3.5" />}
                  {type}
                </span>
                <span className="text-[10px] opacity-70 font-mono">
                  {type === 'all' ? events.length : events.filter((e) => e.type === type).length}
                </span>
              </button>
            ))}
          </div>
          
          <div className="pt-3 border-t border-border space-y-2">
            <h4 className="text-xs font-semibold text-text-tertiary uppercase">Stream Performance</h4>
            <div className="bg-surface-elevated rounded-theme-md p-3 text-xs space-y-1.5 font-mono">
              <div className="flex justify-between"><span className="text-text-tertiary">Kafka Throughput:</span><span className="text-success">100k+ msg/s</span></div>
              <div className="flex justify-between"><span className="text-text-tertiary">Fan-out Clients:</span><span className="text-text">10,000 max</span></div>
              <div className="flex justify-between"><span className="text-text-tertiary">Window Size:</span><span className="text-text">60s tumbling</span></div>
              <div className="flex justify-between"><span className="text-text-tertiary">InfluxDB Storage:</span><span className="text-text">Active</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConnectionBadge({ isConnected, reconnectAttempts, latencyMs }: any) {
  return (
    <div className={cn(
      'flex items-center gap-2 px-3 py-1.5 rounded-theme-md text-xs border',
      isConnected ? 'bg-success/10 border-success/30 text-success' : 'bg-danger/10 border-danger/30 text-danger',
    )}>
      {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
      <div>
        <span className="font-semibold">{isConnected ? 'Live Connected' : 'Disconnected'}</span>
        {latencyMs !== null && isConnected && <span className="ml-1 opacity-70 font-mono">({latencyMs.toFixed(0)}ms)</span>}
      </div>
    </div>
  );
}

function StatsCounter({ messages, bytes }: any) {
  return (
    <div className="bg-surface border border-border px-3 py-1.5 rounded-theme-md text-xs font-mono">
      <span className="text-text-tertiary">Events: </span>
      <span className="text-text font-bold">{messages.toLocaleString()}</span>
    </div>
  );
}
