import { useEffect, useState } from 'react';
import { useWebSocket, buildTelemetryUrl } from '@/lib/websocket';
import { useSimulationStore } from '@/stores/simulationStore';
import type { WSMessage } from '@/types';

export function ConnectionIndicator() {
  const [latency, setLatency] = useState<number | null>(null);
  const updateRobot = useSimulationStore((s) => s.updateRobot);
  const addDetection = useSimulationStore((s) => s.addDetection);
  const addAlert = useSimulationStore((s) => s.addAlert);
  const setSimState = useSimulationStore((s) => s.setSimState);
  const pushTelemetry = useSimulationStore((s) => s.pushTelemetry);

  const { isConnected } = useWebSocket({
    url: buildTelemetryUrl('default'),
    onMessage: (msg: WSMessage) => {
      switch (msg.type) {
        case 'robot_state':
          updateRobot(msg.data);
          break;
        case 'detection':
          addDetection(msg.data);
          break;
        case 'alert':
          addAlert(msg.data);
          break;
        case 'sim_state':
          setSimState(msg.data);
          if (msg.data.environment.co2Concentration) {
            pushTelemetry(msg.data.environment.co2Concentration);
          }
          break;
      }
    },
  });

  useEffect(() => {
    if (!isConnected) return;
    const interval = setInterval(async () => {
      const start = performance.now();
      try {
        await fetch('/api/v1/health/ready');
        setLatency(performance.now() - start);
      } catch {
        setLatency(null);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [isConnected]);

  return (
    <div className="text-xs">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-carbon-400 animate-pulse' : 'bg-critical-500'}`} />
        <span className="text-slate-400">
          {isConnected ? 'Live' : 'Offline'}
        </span>
        {latency !== null && (
          <span className="text-slate-500 font-mono">{latency.toFixed(0)}ms</span>
        )}
      </div>
    </div>
  );
}
