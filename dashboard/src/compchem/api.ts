import { api } from '@/lib/api';

export const compChemApi = {
  runMD: (smiles: string[], n_steps: number, target_T: number) =>
    api.post('/api/v1/compchem/md/run', { smiles, n_molecules: [10], box_size: 25.0, dt: 0.001, n_steps, target_T }).then((r) => r.data),

  runQC: (method: string, functional: string, solvent?: string) =>
    api.post(`/api/v1/compchem/qc/${method}`, {
      atoms: [
        { element: 'O', x: 0, y: 0, z: 0 },
        { element: 'H', x: 0.75, y: 0, z: 0.58 },
        { element: 'H', x: -0.75, y: 0, z: 0.58 },
      ],
      basis_set: 'sto-3g',
      method,
      functional,
      solvent,
    }).then((r) => r.data),

  buildCrystal: (structure_type: string, element?: string) =>
    api.post('/api/v1/compchem/materials/crystal', { structure_type, element: element || 'Na', a: 4.0, b: 4.0 }).then((r) => r.data),

  getPhaseDiagram: (system_name: string) =>
    api.post('/api/v1/compchem/materials/phase-diagram', { system_name, T_min: 300, T_max: 1800 }).then((r) => r.data),
};
