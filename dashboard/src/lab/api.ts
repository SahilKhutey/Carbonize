import { api } from '@/lib/api';

export const labApi = {
  designSolvent: (amine_type: string) =>
    api.post('/api/v1/lab/molecular/solvent/design', { amine_type, additional_groups: [], n_candidates: 5 }).then((r) => r.data),

  designCatalyst: (reaction_type: string) =>
    api.post('/api/v1/lab/molecular/catalyst/design', { target_conversion: 0.95, operating_T: 623.0, reaction_type }).then((r) => r.data),

  createDoE: (design_type: string) =>
    api.post('/api/v1/lab/doe/design', {
      design_type,
      factors: [
        { name: 'Temperature', low: 313, high: 353, units: 'K' },
        { name: 'Pressure', low: 100000, high: 500000, units: 'Pa' },
        { name: 'Concentration', low: 0.1, high: 0.5, units: 'wt%' },
      ],
    }).then((r) => r.data),

  getSamples: () =>
    api.get('/api/v1/lab/lims/samples').then((r) => r.data),

  runHAZOP: () =>
    api.post('/api/v1/lab/safety/hazop/run', { unit_name: 'CO2_Absorber' }).then((r) => r.data),

  generateHypotheses: () =>
    api.post('/api/v1/lab/discovery/hypotheses/generate', {
      data: { results: [{ concentration: 0.3, loading: 0.5 }, { concentration: 0.4, loading: 0.6 }] },
      features: ['concentration', 'loading'],
    }).then((r) => r.data),
};
