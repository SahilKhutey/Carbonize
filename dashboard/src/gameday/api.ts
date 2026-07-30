import { api } from '@/lib/api';

export const gamedayApi = {
  list: () =>
    api.get('/v1/gameday/list').then((r) => r.data),
  
  create: (data: any) =>
    api.post('/v1/gameday/create', data).then((r) => r.data),
  
  run: (id: string) =>
    api.post(`/v1/gameday/${id}/run`).then((r) => r.data),
  
  getStatus: (id: string) =>
    api.get(`/v1/gameday/${id}/status`).then((r) => r.data),
  
  recordAction: (id: string, action: any) =>
    api.post(`/v1/gameday/${id}/action`, action).then((r) => r.data),
};
