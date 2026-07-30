/**
 * High-throughput WebSocket streaming test
 * Simulates 1000+ concurrent stream consumers
 */

import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';

const wsMessages = new Counter('ws_messages_total');
const wsMessageLatency = new Trend('ws_message_latency_ms', true);
const wsErrors = new Counter('ws_errors_total');
const activeConnections = new Gauge('ws_active_connections');
const connectionSuccess = new Rate('ws_connection_success');

export const options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m', target: 500 },
    { duration: '2m', target: 1000 },
    { duration: '1m', target: 500 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    'ws_connection_success': ['rate>0.99'],
    'ws_message_latency_ms': ['p(95)<100', 'p(99)<500'],
  },
};

const WS_URL = __ENV.WS_URL || 'ws://localhost:8080/api/v1/stream/ws';

export default function () {
  const url = WS_URL;
  const startTime = Date.now();
  
  const res = ws.connect(url, {}, function (socket) {
    socket.on('open', () => {
      activeConnections.add(1);
      connectionSuccess.add(true);
      
      socket.send(JSON.stringify({
        type: 'subscribe',
        subscription: {
          robot_id: null,
          metric_types: ['co2_ppm', 'temperature'],
          classes: ['co2_emitter'],
          min_severity: 'info',
        },
      }));
    });
    
    socket.on('message', (data) => {
      wsMessages.add(1);
      try {
        const msg = JSON.parse(data);
        if (msg.type === 'welcome') {
          wsMessageLatency.add(Date.now() - startTime);
        }
      } catch (e) {
        wsErrors.add(1);
      }
    });
    
    socket.on('error', () => {
      wsErrors.add(1);
      connectionSuccess.add(false);
    });
    
    socket.on('close', () => {
      activeConnections.add(-1);
    });
    
    socket.setTimeout(() => socket.close(), 30000);
  });
  
  check(res, {
    'WebSocket connected': (r) => r && r.status === 101,
  });
  
  sleep(1);
}
