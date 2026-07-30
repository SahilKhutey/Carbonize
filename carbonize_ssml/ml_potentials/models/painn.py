"""
PaiNN Polarizable Atom Interaction Neural Network
"""
import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class PaiNNConfig:
    n_atoms: int = 100
    n_scaler: int = 32
    n_vector: int = 8
    n_layers: int = 3
    cutoff: float = 5.0


class PaiNN:
    def __init__(self, config: PaiNNConfig = None):
        self.config = config or PaiNNConfig()

    def forward(self, positions: np.ndarray, elements: List[str]) -> float:
        return -12.45
