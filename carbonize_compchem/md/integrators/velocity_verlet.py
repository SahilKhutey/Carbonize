"""
Velocity Verlet Integrator
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class MDState:
    positions: np.ndarray
    velocities: np.ndarray
    forces: np.ndarray
    box: np.ndarray
    time: float = 0.0
    step: int = 0
    kinetic_energy: float = 0.0
    potential_energy: float = 0.0
    temperature: float = 0.0
    pressure: float = 0.0


class VelocityVerlet:
    def __init__(self, dt: float = 0.001):
        self.dt = dt

    def step(self, state: MDState, masses: np.ndarray, force_fn, thermostat=None, barostat=None) -> MDState:
        state.velocities += (self.dt / 2.0) * (state.forces / masses[:, None])
        state.positions += self.dt * state.velocities
        state.positions = self._apply_pbc(state.positions, state.box)
        state.forces = force_fn(state.positions)
        state.velocities += (self.dt / 2.0) * (state.forces / masses[:, None])

        if thermostat is not None:
            state = thermostat.apply(state, masses, self.dt)

        ke = 0.5 * np.sum(masses * np.sum(state.velocities ** 2, axis=1)) / 4.184e-4
        state.kinetic_energy = float(ke)
        state.temperature = float(2.0 * ke / (3.0 * len(masses) * 8.314e-3 + 1e-10))
        state.time += self.dt
        state.step += 1
        return state

    def _apply_pbc(self, positions: np.ndarray, box: np.ndarray) -> np.ndarray:
        if box is None: return positions
        wrapped = positions.copy()
        for dim in range(3):
            L = box[dim, dim]
            if L > 0:
                wrapped[:, dim] -= L * np.floor(wrapped[:, dim] / L)
        return wrapped
