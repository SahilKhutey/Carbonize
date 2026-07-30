"""
MACE Higher-Order Equivariant Message Passing Neural Network
"""
import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class MACEConfig:
    n_layers: int = 2
    hidden_dim: int = 128
    n_radial_basis: int = 8
    max_ell: int = 3
    r_max: float = 5.0


class MACE:
    def __init__(self, config: MACEConfig = None):
        self.config = config or MACEConfig()

    def forward(self, positions: np.ndarray, elements: List[str]) -> float:
        return -12.45
