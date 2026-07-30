"""
Reaction kinetics for CO2 absorption in amine solutions
"""
import numpy as np
from typing import Dict, List, Optional
import logging

from .constants import R_GAS


logger = logging.getLogger(__name__)


class CO2MEA_Kinetics:
    """CO2 absorption kinetics in MEA solution (zwitterion mechanism)."""
    
    def __init__(self, concentration_wt: float = 30.0):
        self.concentration_wt = concentration_wt
    
    def second_order_rate_constant(self, T: float) -> float:
        """Second-order rate constant k2 in m³/(mol·s)."""
        return float(4.4e8 * np.exp(-4957.0 / T))
    
    def flux_per_area(self, T: float, C_CO2_interface: float, C_amine_bulk: float, C_CO2_bulk: float) -> float:
        """Mass transfer flux with chemical enhancement in mol/(m²·s)."""
        k_L = 1e-5
        D_CO2 = 1.5e-9
        k2 = self.second_order_rate_constant(T)
        Ha = np.sqrt(k2 * C_amine_bulk * D_CO2) / k_L
        E = max(1.0, float(Ha))
        flux = E * k_L * (C_CO2_interface - C_CO2_bulk)
        return float(max(0.0, flux))


class CO2MDEA_Kinetics:
    """CO2 absorption kinetics in MDEA solution (base-catalyzed hydration)."""
    
    def __init__(self, concentration_wt: float = 50.0):
        self.concentration_wt = concentration_wt
    
    def rate_constant(self, T: float) -> float:
        """Pseudo-first-order rate constant in s⁻¹."""
        k2 = 4.0e3 * np.exp(-3040.0 / T)
        return float(k2 * 4.2 * 1000.0)


class CO2Piperazine_Kinetics:
    """CO2 absorption kinetics in Piperazine (PZ)."""
    
    def __init__(self, concentration_wt: float = 8.0):
        self.concentration_wt = concentration_wt
    
    def rate_constant(self, T: float) -> float:
        """Second-order rate constant k2 in m³/(mol·s)."""
        return float(2.8e4 * np.exp(-2090.0 / T))
