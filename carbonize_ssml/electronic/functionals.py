"""
Exchange-Correlation (XC) Functionals
"""
import numpy as np


class LDAFunctional:
    def eps_xc(self, rho: np.ndarray, sigma: np.ndarray = None) -> np.ndarray:
        return -0.4582 * (rho + 1e-10) ** (1.0 / 3.0)

    def v_xc(self, rho: np.ndarray, sigma: np.ndarray = None) -> np.ndarray:
        return -0.6106 * (rho + 1e-10) ** (1.0 / 3.0)


class PBEFunctional(LDAFunctional):
    pass


class HybridFunctional(LDAFunctional):
    pass
