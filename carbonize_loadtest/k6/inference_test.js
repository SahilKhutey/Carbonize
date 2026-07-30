/**
 * ML inference load test — batch + concurrent
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';
import { SharedArray } from 'k6/data';

const inferenceLatency = new Trend('inference_latency_ms', true);
const inferenceSuccess = new Rate('inference_success');

const sampleImages = new SharedArray('images', function () {
  const images = [];
  for (let i = 0; i < 20; i++) {
    images.push('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==');
  }
  return images;
});

export const options = {
  scenarios: {
    light_load: {
      executor: 'constant_arrival_rate',
      rate: 20,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 10,
      maxVUs: 50,
    },
  },
  thresholds: {
    'inference_latency_ms': ['p(95)<300', 'p(99)<600'],
    'inference_success': ['rate>0.98'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const imageB64 = sampleImages[Math.floor(Math.random() * sampleImages.length)];
  const payload = JSON.stringify({
    model_id: '1.5.0',
    image: imageB64,
    confidence_threshold: 0.5,
  });
  
  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/v1/inference/predict`, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
  });
  const latency = Date.now() - start;
  
  const success = check(res, {
    'status 200': (r) => r.status === 200,
  });
  
  inferenceLatency.add(latency);
  inferenceSuccess.add(success);
  sleep(0.1);
}
