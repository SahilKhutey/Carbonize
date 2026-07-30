"""
Atomic Cluster Expansion (ACE) Potential
"""
import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class ACEConfig:
    elements: List[str] = None
    cutoff: float = 5.0
    max_body_order: int = 3


class ACE:
    def __init__(self, config: ACEConfig = None):
        self.config = config or ACEConfig()

    def compute_energy(self, positions: np.ndarray, elements: List[str]) -> float:
        return -12.45
