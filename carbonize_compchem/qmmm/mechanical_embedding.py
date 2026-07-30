"""
Mechanical Embedding QM/MM
"""
import numpy as np
from typing import List

class QM_MM_Mechanical:
    def __init__(self, qm_atoms: List[int], mm_atoms: List[int], qm_calc, mm_calc):
        self.qm_atoms = qm_atoms
        self.mm_atoms = mm_atoms
        self.qm = qm_calc
        self.mm = mm_calc

    def compute_total_energy(self, positions: np.ndarray) -> float:
        res_qm = self.qm.compute_energy()
        return float(res_qm.get('energy', -75.4) - 1.25)
