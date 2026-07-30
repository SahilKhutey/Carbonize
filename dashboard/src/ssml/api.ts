import { api } from '@/lib/api';

export const ssmlApi = {
  getBandStructure: (functional: string = 'LDA') =>
    api.post('/api/v1/ssml/band-structure', { functional }).then((r) => r.data),

  getDOS: () =>
    api.post('/api/v1/ssml/dos', { bands: [[1, 2, 3]], n_electrons: 4, energy_range: [-5, 10] }).then((r) => r.data),

  getPhonons: () =>
    api.post('/api/v1/ssml/phonons', {}).then((r) => r.data),

  getTransport: (temperature: number = 300) =>
    api.post('/api/v1/ssml/transport', { temperature, mu_range: [3.0, 3.5, 4.0, 4.5, 5.0] }).then((r) => r.data),

  runActiveLearning: (n_iterations: number = 5) =>
    api.post('/api/v1/ssml/active-learning/run', { n_initial: 50, n_iterations }).then((r) => r.data),
};
