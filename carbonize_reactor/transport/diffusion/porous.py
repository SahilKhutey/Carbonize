"""
Porous diffusion, Thiele modulus, and internal effectiveness
"""
import numpy as np


def effective_diffusivity(d_p: float, eps_p: float, tau: float, T: float) -> float:
    D_AB = 1.5e-5 * ((T / 298.15)**1.75)
    return float((eps_p / tau) * D_AB)


def thiele_modulus(r: float, k: float, D_eff: float) -> float:
    return float(r * np.sqrt(k / max(D_eff, 1e-15)))


def internal_effectiveness(phi: float, geometry: str = 'sphere') -> float:
    if phi < 0.1:
        return 1.0
    return float((3.0 / phi) * (1.0 / np.tanh(phi) - 1.0 / phi))
