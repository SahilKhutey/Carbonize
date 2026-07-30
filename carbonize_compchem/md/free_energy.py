"""
Free Energy Calculations (FEP, TI, Umbrella Sampling)
"""
import numpy as np

class FreeEnergyPerturbation:
    def compute_dG(self, dE_lambda: np.ndarray, T: float = 300.0) -> float:
        k_B = 8.314e-3
        beta = 1.0 / (k_B * T)
        return float(-1.0 / beta * np.log(np.mean(np.exp(-beta * dE_lambda))))
