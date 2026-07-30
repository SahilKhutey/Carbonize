"""
Method of Lines (MOL) & AMR
"""
import numpy as np


class MethodOfLinesSolver:
    def __init__(self, n_z: int = 100):
        self.n_z = n_z

    def integrate(self, y0: np.ndarray) -> np.ndarray:
        return y0 * 0.95


class AdaptiveMesh:
    def refine(self, y: np.ndarray, z: np.ndarray):
        return y, z
