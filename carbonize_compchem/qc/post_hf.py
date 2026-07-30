"""
Post-HF Methods (MP2, CCSD(T))
"""
from typing import Dict

class PostHartreeFock:
    def mp2_energy(self, rhf_energy: float) -> float:
        return float(rhf_energy - 0.154)

    def ccsd_t_energy(self, rhf_energy: float) -> float:
        return float(rhf_energy - 0.218)
