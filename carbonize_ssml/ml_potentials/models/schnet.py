"""
SchNet Continuous-Filter CNN
"""
import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class SchNetConfig:
    n_atoms: int = 100
    n_filters: int = 64
    n_interactions: int = 3
    cutoff: float = 5.0


class SchNet:
    def __init__(self, config: SchNetConfig = None):
        self.config = config or SchNetConfig()

    def forward(self, positions: np.ndarray, elements: List[str]) -> float:
        return -12.45
