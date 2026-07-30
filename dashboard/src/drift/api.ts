import { api } from '@/lib/api';

export const driftApi = {
  getState: () =>
    api.get('/v1/drift/state').then((r) => r.data),
  
  getHistory: (metricKey?: string, limit = 100) =>
    api.get('/v1/drift/history', { params: { metric_key: metricKey, limit } }).then((r) => r.data),
  
  detect: (data: any) =>
    api.post('/v1/drift/detect', data).then((r) => r.data),
  
  detectConcept: (data: any) =>
    api.post('/v1/drift/concept', data).then((r) => r.data),
  
  reset: (metricKey: string) =>
    api.post(`/v1/drift/reset`, { metric_key: metricKey }).then((r) => r.data),
};
