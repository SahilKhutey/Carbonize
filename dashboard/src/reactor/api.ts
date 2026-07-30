import { api } from '@/lib/api';

export const reactorApi = {
  solveReactor: (data: { reactor_type: string; length: number; diameter: number; T_in: number; P_in: number; flow_gas: number }) =>
    api.post('/v1/reactor/solve', data).then((r) => r.data),
  
  getThiele: (r: number, k: number, D_eff: number) =>
    api.get(`/v1/reactor/thiele?r=${r}&k=${k}&D_eff=${D_eff}`).then((r) => r.data),
};
