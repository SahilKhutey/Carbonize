"""
Vapor-Liquid Equilibrium for CO2-amine systems
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from .constants import R_GAS


logger = logging.getLogger(__name__)


@dataclass
class VLEResult:
    """Result of VLE calculation."""
    P: float
    T: float
    x_CO2: float
    y_CO2: float
    loading: float
    partial_pressure_CO2: float
    henry_constant: float
    equilibrium_constant: float


class CO2AmineVLE:
    """CO2-amine vapor-liquid equilibrium (Kent-Eisenberg model)."""
    
    def __init__(self, amine: str = 'MEA', concentration_wt: float = 30.0):
        self.amine = amine
        self.concentration_wt = concentration_wt
        self.amine_mw = {'MEA': 61.08, 'MDEA': 119.16, 'Piperazine': 86.14, 'KS1': 396.0}.get(amine, 61.08)
    
    def henry_constant_co2_water(self, T: float) -> float:
        """Henry's constant for CO2 in pure water (Pa)."""
        ln_H = -6.8346 + 1.2817e4 / T - 3.7668e6 / T**2 + 2.997e8 / T**3
        return float(np.exp(ln_H) * 1e6)
    
    def equilibrium_pressure(self, T: float, loading: float) -> float:
        """Calculate CO2 partial pressure (Pa) over loaded amine solution."""
        loading = max(0.001, min(loading, 2.0))
        H = self.henry_constant_co2_water(T)
        
        if self.amine == 'MEA':
            K1 = np.exp(-6.12484 - 0.012192 * T + 0.0001387 * T**2)
            K2 = 1e8 * np.exp(-9090.0 / T + 4.0)
        else:
            K1 = np.exp(-7.444 + 0.0046 * T)
            K2 = 1e7 * np.exp(-8500.0 / T + 3.5)
        
        K2_L = K2 * loading
        K1_alpha = K1 * loading
        
        if K1_alpha >= 1.0:
            return 1e7
        
        numerator = H * loading**2 * K1 * K2 / (1 + K2_L)
        p_CO2 = numerator / (1 - K1_alpha)
        return float(max(1.0, p_CO2))
    
    def loading_from_partial_pressure(self, T: float, P_CO2: float) -> float:
        """Estimate loading from CO2 partial pressure (Pa)."""
        # Invert equilibrium pressure using bisection
        low, high = 0.001, 1.5
        for _ in range(30):
            mid = (low + high) / 2.0
            p_mid = self.equilibrium_pressure(T, mid)
            if p_mid < P_CO2:
                low = mid
            else:
                high = mid
        return float((low + high) / 2.0)
