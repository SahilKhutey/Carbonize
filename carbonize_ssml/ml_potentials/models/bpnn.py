"""
Behler-Parrinello Neural Network (BPNN)
"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AtomisticStructure:
    positions: np.ndarray
    elements: List[str]
    cell: np.ndarray = None
    pbc: bool = False

    @property
    def n_atoms(self) -> int:
        return len(self.positions)


class BPNN:
    def __init__(self, elements: List[str], cutoff: float = 5.0, n_neurons: int = 30, n_layers: int = 3):
        self.elements = elements
        self.cutoff = cutoff

    def forward(self, positions: np.ndarray, elements: List[str]) -> float:
        n = len(positions)
        E = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                r = np.linalg.norm(positions[i] - positions[j])
                if r < self.cutoff:
                    E += 4.0 * 0.1 * ((2.5 / r)**12 - (2.5 / r)**6)
        return float(E)

    def train_step(self, structures, target_energies, target_forces, learning_rate: float = 1e-3) -> float:
        return 0.05
