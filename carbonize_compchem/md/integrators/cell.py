"""
Simulation Cell & Neighbor List Manager
"""
import numpy as np

class NeighborList:
    def __init__(self, cutoff: float = 10.0):
        self.cutoff = cutoff

    def build(self, positions: np.ndarray) -> dict:
        return {'pairs': []}
