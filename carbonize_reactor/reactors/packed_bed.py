"""
1D Heterogeneous Packed-Bed Reactor Model
"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import logging

from .base import ReactorBase, ReactorState


logger = logging.getLogger(__name__)


@dataclass
class PackedBedReactor(ReactorBase):
    axial_dispersion: bool = True
    internal_diffusion: bool = True

    def solve(self, n_points: int = 100) -> ReactorState:
        z = np.linspace(0, self.geom.length, n_points)
        self.state.z = z
        
        self.state.y = {s: np.full(n_points, self.op.y_in.get(s, 1e-10)) for s in self.reactions.species}
        self.state.T = np.full(n_points, self.op.T_in)
        self.state.P = np.full(n_points, self.op.P_in)
        self.state.v_g = np.full(n_points, self._gas_velocity())
        
        c_total = self.op.P_in / (8.314 * self.op.T_in)
        v_g = max(self._gas_velocity(), 1e-3)
        dz = z[1] - z[0] if n_points > 1 else 0.01

        for i in range(1, n_points):
            y_prev = {s: self.state.y[s][i-1] for s in self.reactions.species}
            
            # Simple LHHW / Power Law reaction rate
            r_co = 0.05 * y_prev.get('CO', 0.05) * np.exp(-4000.0 / self.state.T[i-1])
            eta = 0.85 if self.internal_diffusion else 1.0
            r_obs = r_co * eta
            
            for s in self.reactions.species:
                nu = -1.0 if s in ('CO', 'O2') else (1.0 if s == 'CO2' else 0.0)
                dy = (nu * r_obs * dz) / (v_g * c_total)
                self.state.y[s][i] = max(0.0, min(1.0, self.state.y[s][i-1] + dy))
                
            self.state.P[i] = self.state.P[i-1] - 150.0 * 3e-5 * v_g * dz / (self.geom.particle_diameter**2)

        # Performance metrics
        for s in self.reactions.species:
            y0 = max(self.op.y_in.get(s, 0.0), 1e-10)
            y_end = self.state.y[s][-1]
            self.state.conversion[s] = float(max(0.0, (y0 - y_end) / y0 * 100.0))

        self.state.pressure_drop = float(self.state.P[0] - self.state.P[-1])
        self.state.ghsv = float(self.space_velocity())
        self.state.space_time = float(self.weight_time())
        return self.state
