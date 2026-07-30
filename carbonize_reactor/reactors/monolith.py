"""
Monolith (Honeycomb) Reactor Model
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass
from .base import ReactorBase, ReactorState


@dataclass
class MonolithReactor(ReactorBase):
    channel_shape: str = 'square'
    washcoat_thickness: float = 0.00005

    def solve(self, n_points: int = 100) -> ReactorState:
        z = np.linspace(0, self.geom.length, n_points)
        self.state.z = z
        self.state.y = {s: np.full(n_points, self.op.y_in.get(s, 1e-10)) for s in self.reactions.species}
        self.state.T = np.full(n_points, self.op.T_in)
        self.state.P = np.full(n_points, self.op.P_in)

        dz = z[1] - z[0] if n_points > 1 else 0.01
        for i in range(1, n_points):
            for s in self.reactions.species:
                decay = 0.015 * self.state.y[s][i-1] * dz
                self.state.y[s][i] = max(0.0, self.state.y[s][i-1] - decay)

        for s in self.reactions.species:
            y0 = max(self.op.y_in.get(s, 0.0), 1e-10)
            self.state.conversion[s] = float(max(0.0, (y0 - self.state.y[s][-1]) / y0 * 100.0))
        return self.state
