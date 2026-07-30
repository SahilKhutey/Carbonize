import { api } from '@/lib/api';

const DEMO_BASE = '/api/v1/demo';

export const demoApi = {
  getOverview: () => api.get(`${DEMO_BASE}/overview`).then((r) => r.data),
  getSolvents: (params?: any) => api.get(`${DEMO_BASE}/solvents`, { params }).then((r) => r.data),
  getSolvent: (id: string) => api.get(`${DEMO_BASE}/solvents/${id}`).then((r) => r.data),
  compareSolvents: (id: string, baseline: string) =>
    api.get(`${DEMO_BASE}/solvents/${id}/compare/${baseline}`).then((r) => r.data),
  getOperations: (params?: any) => api.get(`${DEMO_BASE}/operations`, { params }).then((r) => r.data),
  getLabResults: () => api.get(`${DEMO_BASE}/lab-results`).then((r) => r.data),
  getChaosResults: () => api.get(`${DEMO_BASE}/chaos-results`).then((r) => r.data),
  calculateROI: (data: any) => api.post(`${DEMO_BASE}/roi/calculate`, data).then((r) => r.data),
  getComparison: () => api.get(`${DEMO_BASE}/comparison`).then((r) => r.data),
  getProposal: () => api.get(`${DEMO_BASE}/proposal`).then((r) => r.data),
  submitProposal: (data: any) => api.post(`${DEMO_BASE}/proposal`, data).then((r) => r.data),
  getTourSteps: () => api.get(`${DEMO_BASE}/tour/steps`).then((r) => r.data),
};

export default demoApi;
