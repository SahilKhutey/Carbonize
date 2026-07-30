/**
 * Carbonize Main Load Test
 * Tests: REST API, inference, telemetry ingestion
 * 
 * Usage:
 *   k6 run --out json=results/main.json k6/load_test.js
 *   k6 run --vus 100 --duration 10m k6/load_test.js
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep, group, fail } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// ─── Custom Metrics ─────────────────────────────────────────────
const inferenceLatency = new Trend('inference_latency_ms', true);
const inferenceSuccess = new Rate('inference_success_rate');
const inferenceP99 = new Trend('inference_p99', true);
const telemetryIngestion = new Counter('telemetry_ingested_total');
const wsConnections = new Gauge('ws_active_connections');
const wsMessages = new Counter('ws_messages_received');
const apiErrors = new Counter('api_errors_total');
const dataTransferred = new Counter('data_transferred_bytes');

// ─── Test data ─────────────────────────────────────────────────
const testImages = new SharedArray('test_images', function () {
  const images = [];
  for (let i = 0; i < 50; i++) {
    const fakeImage = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    images.push(fakeImage);
  }
  return images;
});

// ─── Configuration ─────────────────────────────────────────────
export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 200 },
    { duration: '5m', target: 500 },
    { duration: '3m', target: 1000 },
    { duration: '5m', target: 1000 },
    { duration: '2m', target: 500 },
    { duration: '1m', target: 0 },
  ],
  
  thresholds: {
    'http_req_duration{endpoint:health}': ['p(95)<50', 'p(99)<100'],
    'http_req_duration{endpoint:inference}': ['p(95)<200', 'p(99)<500'],
    'http_req_duration{endpoint:telemetry}': ['p(95)<100', 'p(99)<200'],
    'inference_success_rate': ['rate>0.99'],
    'http_req_failed': ['rate<0.01'],
    'inference_latency_ms': ['p(95)<200', 'p(99)<500'],
  },
  
  tags: {
    testid: `carbonize-${Date.now()}`,
    environment: __ENV.ENV || 'staging',
  },
};

export function setup() {
  const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
  const WS_URL = __ENV.WS_URL || 'ws://localhost:8000/api/v1/stream/ws';
  
  return {
    baseUrl: BASE_URL,
    wsUrl: WS_URL,
    token: 'test-token',
    modelId: '1.5.0',
    robotIds: ['robot_1', 'robot_2', 'robot_3', 'robot_4', 'robot_5'],
  };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };
  
  const scenario = Math.floor(Math.random() * 100) + 1;
  
  if (scenario <= 60) {
    inferenceScenario(data, headers);
  } else if (scenario <= 80) {
    telemetryScenario(data, headers);
  } else if (scenario <= 90) {
    analyticsScenario(data, headers);
  } else {
    predictionScenario(data, headers);
  }
}

function inferenceScenario(data, headers) {
  group('inference', () => {
    const imageB64 = testImages[Math.floor(Math.random() * testImages.length)];
    const payload = JSON.stringify({
      model_id: data.modelId,
      image: imageB64,
      confidence_threshold: 0.5,
      iou_threshold: 0.45,
    });
    
    const start = Date.now();
    const res = http.post(`${data.baseUrl}/api/v1/inference/predict`, payload, {
      headers,
      tags: { endpoint: 'inference' },
      timeout: '30s',
    });
    const duration = Date.now() - start;
    
    const success = check(res, {
      'inference status 200': (r) => r.status === 200,
    });
    
    inferenceLatency.add(duration);
    inferenceSuccess.add(success);
    inferenceP99.add(duration);
    if (res.body) dataTransferred.add(res.body.length);
  });
  
  sleep(0.2);
}

function telemetryScenario(data, headers) {
  group('telemetry', () => {
    const robotId = data.robotIds[Math.floor(Math.random() * data.robotIds.length)];
    const metrics = ['co2_ppm', 'temperature', 'humidity', 'battery'];
    const metric = metrics[Math.floor(Math.random() * metrics.length)];
    
    const payload = JSON.stringify({
      robot_id: robotId,
      metric_type: metric,
      value: Math.random() * 1000,
      timestamp: Date.now(),
      source: 'loadtest',
    });
    
    const res = http.post(`${data.baseUrl}/api/v1/telemetry`, payload, {
      headers,
      tags: { endpoint: 'telemetry' },
      timeout: '10s',
    });
    
    check(res, {
      'telemetry status 200/202': (r) => r.status === 200 || r.status === 202,
    });
    
    telemetryIngestion.add(1);
  });
  
  sleep(0.1);
}

function analyticsScenario(data, headers) {
  group('analytics', () => {
    const res = http.get(`${data.baseUrl}/api/v1/analytics/metrics/co2_capture?range=-1h&window=1m`, {
      headers,
      tags: { endpoint: 'analytics' },
      timeout: '15s',
    });
    
    check(res, {
      'analytics status 200': (r) => r.status === 200,
    });
  });
  
  sleep(0.5);
}

function predictionScenario(data, headers) {
  group('prediction', () => {
    const payload = JSON.stringify({
      name: `LoadTest forecast ${Date.now()}`,
      metric_type: 'co2_capture',
      horizon_hours: 1,
      forecast_model: 'prophet',
    });
    
    const res = http.post(`${data.baseUrl}/api/v1/predictions`, payload, {
      headers,
      tags: { endpoint: 'prediction' },
      timeout: '30s',
    });
    
    check(res, {
      'prediction status 200/201': (r) => r.status === 200 || r.status === 201,
    });
  });
  
  sleep(1.0);
}
