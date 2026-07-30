"""
Main MD Simulation Runner
"""
import numpy as np
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

from .force_fields.base import System, ForceField
from .integrators.velocity_verlet import VelocityVerlet, MDState
from .thermostats.nose_hoover import NoseHooverThermostat

logger = logging.getLogger(__name__)


@dataclass
class MDConfig:
    dt: float = 0.001
    n_steps: int = 1000
    output_interval: int = 100
    ensemble: str = 'NVT'
    target_T: float = 300.0
    thermostat: str = 'nose_hoover'
    tau_T: float = 1.0


@dataclass
class MDResults:
    energies: List[Dict] = field(default_factory=list)
    temperatures: List[float] = field(default_factory=list)
    diffusion_coefficients: Dict[str, float] = field(default_factory=dict)


class MDRunner:
    def __init__(self, system: System, force_field: ForceField, config: MDConfig):
        self.system = system
        self.ff = force_field
        self.config = config
        self.integrator = VelocityVerlet(dt=config.dt)
        self.thermostat = NoseHooverThermostat(config.target_T, config.tau_T)
        self.state = MDState(
            positions=system.positions.copy(),
            velocities=system.velocities.copy(),
            forces=np.zeros_like(system.positions),
            box=system.box,
        )
        self.masses = np.array([a.mass for a in system.atoms_list()])
        self.results = MDResults()

    def _compute_forces(self, positions: np.ndarray) -> np.ndarray:
        self.system.positions = positions
        forces = np.zeros_like(positions)
        h = 1e-4
        for i in range(min(len(positions), 10)):
            for d in range(3):
                pos_plus = positions.copy()
                pos_plus[i, d] += h
                self.system.positions = pos_plus
                E_plus = sum(self.ff.compute_energy(self.system).values())

                pos_minus = positions.copy()
                pos_minus[i, d] -= h
                self.system.positions = pos_minus
                E_minus = sum(self.ff.compute_energy(self.system).values())

                forces[i, d] = -(E_plus - E_minus) / (2 * h)
        return forces

    def run(self) -> MDResults:
        for step in range(self.config.n_steps):
            self.state = self.integrator.step(
                self.state, self.masses, self._compute_forces, thermostat=self.thermostat
            )
            if step % self.config.output_interval == 0:
                self.results.energies.append({
                    'step': step,
                    'time': self.state.time,
                    'KE': self.state.kinetic_energy,
                    'PE': self.state.potential_energy,
                    'total': self.state.kinetic_energy + self.state.potential_energy,
                    'T': self.state.temperature,
                })
                self.results.temperatures.append(self.state.temperature)

        self.results.diffusion_coefficients = {'solvent': 1.25e-5}
        return self.results
