"""
Trickle-Bed Reactor (3-Phase G/L/S)
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass
from .base import ReactorBase, ReactorState


class TrickleBedReactor(ReactorBase):
    def __init__(self, geometry, operating, reactions, liquid_velocity: float = 0.001, wetting_efficiency: float = 0.85):
        super().__init__(geometry, operating, reactions)
        self.liquid_velocity = liquid_velocity
        self.wetting_efficiency = wetting_efficiency

    def solve(self, n_points: int = 100) -> ReactorState:
        z = np.linspace(0, self.geom.length, n_points)
        self.state.z = z
        self.state.y = {s: np.full(n_points, self.op.y_in.get(s, 1e-10)) for s in self.reactions.species}
        self.state.T = np.full(n_points, self.op.T_in)
        self.state.P = np.full(n_points, self.op.P_in)
        
        dz = z[1] - z[0] if n_points > 1 else 0.01
        for i in range(1, n_points):
            for s in self.reactions.species:
                loss = 0.01 * self.state.y[s][i-1] * self.wetting_efficiency * dz
                self.state.y[s][i] = max(0.0, self.state.y[s][i-1] - loss)

        for s in self.reactions.species:
            y0 = max(self.op.y_in.get(s, 0.0), 1e-10)
            self.state.conversion[s] = float(max(0.0, (y0 - self.state.y[s][-1]) / y0 * 100.0))
        return self.state
