import { api } from '@/lib/api';

export const predictionsApi = {
  create: (data: any) =>
    api.post('/v1/predictions', data).then((r) => r.data),
  
  list: (params?: any) =>
    api.get('/v1/predictions', { params }).then((r) => r.data),
  
  get: (id: string) =>
    api.get(`/v1/predictions/${id}`).then((r) => r.data),
  
  whatIf: (scenario: any) =>
    api.post('/v1/predictions/what-if', scenario).then((r) => r.data),
  
  delete: (id: string) =>
    api.delete(`/v1/predictions/${id}`).then((r) => r.data),
};
