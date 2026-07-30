"""
Crystal Structure Prediction and Analysis
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class CrystalStructure:
    name: str
    lattice: np.ndarray = None
    basis: List[Dict] = field(default_factory=list)
    spacegroup: str = 'P1'

    def __post_init__(self):
        if self.lattice is None:
            self.lattice = np.eye(3)

    @property
    def volume(self) -> float:
        return float(abs(np.linalg.det(self.lattice)))


class CrystalBuilder:
    @staticmethod
    def rock_salt(element: str = 'Na') -> CrystalStructure:
        a = 5.64
        lattice = a * np.eye(3)
        basis = [
            {'element': element, 'position': [0.0, 0.0, 0.0]},
            {'element': 'Cl', 'position': [0.5, 0.5, 0.5]},
        ]
        return CrystalStructure(name=f'RockSalt_{element}', lattice=lattice, basis=basis)

    @staticmethod
    def perovskite(a: float = 4.0, b: float = 4.0) -> CrystalStructure:
        lattice = np.diag([a, a, b])
        basis = [
            {'element': 'Ca', 'position': [0.0, 0.0, 0.0]},
            {'element': 'Ti', 'position': [0.5, 0.5, 0.5]},
            {'element': 'O', 'position': [0.5, 0.5, 0.0]},
        ]
        return CrystalStructure(name='Perovskite', lattice=lattice, basis=basis)

    @staticmethod
    def graphite(c: float = 6.71, a: float = 2.46) -> CrystalStructure:
        lattice = np.diag([a, a, c])
        basis = [{'element': 'C', 'position': [0.0, 0.0, 0.0]}]
        return CrystalStructure(name='Graphite', lattice=lattice, basis=basis)
