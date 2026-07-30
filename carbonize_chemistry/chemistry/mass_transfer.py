"""
Two-film theory and multi-component mass transfer
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .constants import R_GAS
from .thermodynamics import diffusivity_gas, diffusivity_liquid, viscosity_gas, viscosity_liquid


@dataclass
class MassTransferParams:
    k_G: float
    k_L: float
    a: float
    f: float = 0.0
    H: float = 1.0
    
    @property
    def K_G(self) -> float:
        if self.f == 0 or self.k_L == 0:
            return self.k_G
        return 1.0 / (1.0 / self.k_G + 1.0 / (self.H * self.f * self.k_L + 1e-10))


class TwoFilmTheory:
    """Two-film mass transfer theory implementation."""
    
    def calculate_k_g(self, compound: str, T: float, P: float, v_gas: float, d_p: float) -> float:
        """Gas-side mass transfer coefficient (m/s)."""
        Re = 1.2 * v_gas * d_p / (viscosity_gas('Air', T) + 1e-10)
        Sc = viscosity_gas('Air', T) / (1.2 * diffusivity_gas(compound, 'Air', T, P) + 1e-10)
        Sh = 0.023 * (Re**0.83) * (Sc**0.44)
        return float(Sh * diffusivity_gas(compound, 'Air', T, P) / d_p)
    
    def calculate_k_l(self, T: float, d_p: float, v_liquid: float, compound_l: str = 'CO2', solvent: str = 'H2O') -> float:
        """Liquid-side mass transfer coefficient (Onda correlation, m/s)."""
        mu_L = viscosity_liquid(solvent, T)
        rho_L = 1000.0
        D_L = diffusivity_liquid(compound_l, solvent, T)
        g = 9.81
        k_L = 0.0051 * ((g * rho_L**2 / (mu_L + 1e-10))**(2.0/3.0)) * (D_L**(2.0/3.0)) * (d_p**(-0.4))
        return float(k_L)
    
    def enhancement_factor(self, Ha: float) -> float:
        """Chemical absorption enhancement factor."""
        if Ha < 0.02:
            return 1.0
        if Ha > 3.0:
            return float(Ha)
        ha2 = Ha**2
        term = ha2 / (2.0 * (1.0 - np.exp(-ha2)))
        return float(-term + np.sqrt(term**2 + 1.0))
