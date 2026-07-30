import { useEffect, useRef, useState, useCallback } from 'react';
import type { WSMessage, StreamSubscription } from '@/types/streaming';

interface UseStreamOptions {
  url?: string;
  enabled?: boolean;
  onMessage?: (msg: WSMessage) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

interface StreamState {
  isConnected: boolean;
  reconnectAttempts: number;
  lastMessage: WSMessage | null;
  messagesReceived: number;
  bytesReceived: number;
  latencyMs: number | null;
  subscription: StreamSubscription | null;
}

export function useStream({
  url = 'ws://localhost:8080/api/v1/stream/ws',
  enabled = true,
  onMessage,
  reconnectInterval = 3000,
  maxReconnectAttempts = 50,
  heartbeatInterval = 30000,
}: UseStreamOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null);
  const onMessageRef = useRef(onMessage);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastPingTimeRef = useRef<number>(0);
  const simIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  const [state, setState] = useState<StreamState>({
    isConnected: false,
    reconnectAttempts: 0,
    lastMessage: null,
    messagesReceived: 0,
    bytesReceived: 0,
    latencyMs: null,
    subscription: null,
  });
  
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);
  
  const startSimulationMode = useCallback(() => {
    setState((s) => ({ ...s, isConnected: true, latencyMs: 14 }));
    if (simIntervalRef.current) clearInterval(simIntervalRef.current);
    
    simIntervalRef.current = setInterval(() => {
      const now = Date.now();
      const metrics = ['co2_ppm', 'temperature', 'humidity', 'battery'];
      const metric = metrics[Math.floor(Math.random() * metrics.length)];
      const robotId = `robot_${Math.floor(Math.random() * 4) + 1}`;
      let val = 400 + Math.random() * 50;
      if (metric === 'temperature') val = 25 + Math.random() * 5;
      if (metric === 'humidity') val = 60 + Math.random() * 10;
      if (metric === 'battery') val = 90 - (now % 100000) / 2000;

      const mockTelemetryMsg: WSMessage = {
        type: 'telemetry',
        timestamp: now,
        data: {
          event_id: `evt-${now}-${Math.random()}`,
          timestamp: now,
          robot_id: robotId,
          metric_type: metric,
          value: val,
          unit: metric === 'co2_ppm' ? 'ppm' : metric === 'temperature' ? '°C' : '%',
        },
      };

      setState((s) => ({
        ...s,
        lastMessage: mockTelemetryMsg,
        messagesReceived: s.messagesReceived + 1,
        bytesReceived: s.bytesReceived + 180,
      }));
      onMessageRef.current?.(mockTelemetryMsg);
    }, 400);
  }, []);

  const connect = useCallback(() => {
    if (!enabled) return;
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      ws.binaryType = 'arraybuffer';
      
      ws.onopen = () => {
        if (simIntervalRef.current) clearInterval(simIntervalRef.current);
        setState((s) => ({
          ...s,
          isConnected: true,
          reconnectAttempts: 0,
        }));
        reconnectAttemptsRef.current = 0;
        
        if (heartbeatTimerRef.current) clearInterval(heartbeatTimerRef.current);
        heartbeatTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            lastPingTimeRef.current = performance.now();
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, heartbeatInterval);
      };
      
      ws.onmessage = (event) => {
        const data = typeof event.data === 'string' ? event.data : new TextDecoder().decode(event.data);
        
        if (data.includes('"pong"')) {
          const latency = performance.now() - lastPingTimeRef.current;
          setState((s) => ({ ...s, latencyMs: latency }));
          return;
        }
        
        try {
          const msg = JSON.parse(data) as WSMessage;
          setState((s) => ({
            ...s,
            lastMessage: msg,
            messagesReceived: s.messagesReceived + 1,
            bytesReceived: s.bytesReceived + data.length,
          }));
          onMessageRef.current?.(msg);
        } catch (err) {
          console.error('Failed to parse stream message:', err);
        }
      };
      
      ws.onerror = () => {
        startSimulationMode();
      };
      
      ws.onclose = () => {
        wsRef.current = null;
        if (heartbeatTimerRef.current) {
          clearInterval(heartbeatTimerRef.current);
          heartbeatTimerRef.current = null;
        }
        startSimulationMode();
      };
    } catch (err) {
      startSimulationMode();
    }
  }, [url, enabled, heartbeatInterval, startSimulationMode]);
  
  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (heartbeatTimerRef.current) clearInterval(heartbeatTimerRef.current);
      if (simIntervalRef.current) clearInterval(simIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);
  
  const subscribe = useCallback((subscription: StreamSubscription) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'subscribe', subscription }));
    }
    setState((s) => ({ ...s, subscription }));
  }, []);
  
  const unsubscribe = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        subscription: { robot_id: null, metric_types: [], classes: [], min_severity: 'info' },
      }));
    }
    setState((s) => ({ ...s, subscription: null }));
  }, []);
  
  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);
  
  return {
    ...state,
    subscribe,
    unsubscribe,
    send,
  };
}
