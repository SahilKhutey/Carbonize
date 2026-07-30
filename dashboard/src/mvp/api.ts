import { api } from '@/lib/api';

export const mvpApi = {
  getDemoSeed: () =>
    api.get('/api/v1/mvp/demo/seed').then((r) => r.data),

  calculateROI: (capacity_t_yr: number, steam_cost_usd_gj: number) =>
    api.post('/api/v1/mvp/roi/calculate', { capacity_t_yr, steam_cost_usd_gj }).then((r) => r.data),

  getArchitecture: (tier: string = 'medium') =>
    api.get(`/api/v1/mvp/architecture/reference?tier=${tier}`).then((r) => r.data),

  getPitchDeck: () =>
    api.get('/api/v1/mvp/sales/pitch-deck').then((r) => r.data),
};
