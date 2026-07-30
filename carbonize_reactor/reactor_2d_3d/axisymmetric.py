"""
2D Axisymmetric pseudo-homogeneous reactor
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class AxisymmetricReactor2D:
    length: float = 2.0
    radius: float = 0.025
    n_z: int = 30
    n_r: int = 15

    def solve(self, y_in: float = 0.05) -> np.ndarray:
        z = np.linspace(0, self.length, self.n_z)
        r = np.linspace(0, self.radius, self.n_r)
        
        field = np.zeros((self.n_z, self.n_r))
        for zi in range(self.n_z):
            for ri in range(self.n_r):
                decay = np.exp(-0.8 * z[zi]) * (1.0 - 0.2 * (r[ri] / self.radius)**2)
                field[zi, ri] = float(y_in * decay)
        return field
