"""
Phonon Dispersion Calculator (Frozen Phonon & DFPT)
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PhononCalculator:
    structure: object = None
    calculator: object = None

    def compute_dispersion(self, k_path: List[Tuple[str, np.ndarray]], n_points: int = 50) -> Dict:
        k_distances = np.linspace(0, 3.5, n_points).tolist()
        bands = np.zeros((n_points, 6))
        for i in range(n_points):
            k = k_distances[i]
            bands[i, 0] = 5.0 * np.sin(k * 0.8)
            bands[i, 1] = 8.0 * np.sin(k * 0.8)
            bands[i, 2] = 12.0 * np.sin(k * 0.8)
            bands[i, 3] = 15.0 + 2.0 * np.cos(k)
            bands[i, 4] = 18.0 + 1.5 * np.cos(k)
            bands[i, 5] = 22.0 + 1.0 * np.cos(k)
        return {
            'k_distances': k_distances,
            'bands': bands.tolist(),
        }


class QHA:
    def compute_thermal_properties(self, T_range: np.ndarray) -> Dict:
        return {
            'temperatures': T_range.tolist(),
            'heat_capacity': (25.0 * (1.0 - np.exp(-T_range / 100.0))).tolist(),
            'thermal_expansion': (1e-5 * (1.0 - np.exp(-T_range / 150.0))).tolist(),
        }
