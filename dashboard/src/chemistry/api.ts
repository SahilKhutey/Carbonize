import { api } from '@/lib/api';

export const chemistryApi = {
  getVleEquilibrium: (data: { amine: string; concentration_wt: number; T: number; loading: number }) =>
    api.post('/v1/chemistry/vle/equilibrium', data).then((r) => r.data),
  
  calculateSox: (data: { gas_flow_nm3_h: number; SO2_in_ppm: number; SO3_in_ppm: number; scrubber_type: string }) =>
    api.post('/v1/chemistry/pollutants/sox', data).then((r) => r.data),
  
  calculateNox: (data: { gas_flow_nm3_h: number; NO_in_ppm: number; system_type: string }) =>
    api.post('/v1/chemistry/pollutants/nox', data).then((r) => r.data),
  
  calculateMercury: (data: { gas_flow_nm3_h: number; Hg_in_ug_Nm3: number }) =>
    api.post('/v1/chemistry/pollutants/mercury', data).then((r) => r.data),
  
  simulatePlant: (durationMinutes: number = 10) =>
    api.post(`/v1/chemistry/plant/simulate?duration_minutes=${durationMinutes}`).then((r) => r.data),
};
