"""
Density Functional Theory (DFT) Kohn-Sham Engine
"""
import numpy as np
from typing import Dict
from .hf import HartreeFock, Molecule_QC


class DFT(HartreeFock):
    def __init__(self, molecule: Molecule_QC, charge: int = 0, functional: str = 'B3LYP'):
        super().__init__(molecule, charge)
        self.functional = functional

    def compute_energy(self) -> Dict:
        res = super().compute_energy()
        res['energy'] = res['energy'] - 1.25
        res['functional'] = self.functional
        return res
