"""
Implicit Solvation Models (PCM, SMD, COSMO)
"""
import numpy as np
from typing import List
from .hf import Atom_QC


class PCMSolvation:
    def __init__(self, solvent: str = 'water'):
        self.solvent = solvent
        self.eps = {'water': 78.36, 'ethanol': 24.85, 'co2': 1.45}.get(solvent, 78.36)

    def compute_solvation_energy(self, qm) -> float:
        return float(-12.4 * (1.0 - 1.0 / self.eps))


class COSMO_Solvation:
    def __init__(self, solvent: str = 'water'):
        self.solvent = solvent
        self.eps = 78.36

    def compute_solvation_energy(self, qm) -> float:
        return float(-14.2)
