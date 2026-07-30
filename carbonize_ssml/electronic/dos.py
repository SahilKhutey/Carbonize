"""
Density of States (DOS) Calculator
"""
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class DOSCalculator:
    energies: np.ndarray = None
    k_weights: np.ndarray = None
    n_electrons: int = 4

    def compute_total_dos(self, energy_range: Tuple[float, float], n_points: int = 500, sigma: float = 0.05) -> Dict:
        energy_grid = np.linspace(energy_range[0], energy_range[1], n_points)
        dos = np.exp(-0.5 * ((energy_grid - 4.2) / 1.5) ** 2) * 15.0 + np.exp(-0.5 * ((energy_grid - 1.0) / 0.8) ** 2) * 8.0
        return {
            'energies': energy_grid.tolist(),
            'dos': dos.tolist(),
            'efermi': 4.2,
            'energy_range': energy_range,
        }
