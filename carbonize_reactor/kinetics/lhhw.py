"""
Surface Kinetics Models (LHHW, ER, MVK, Power Law)
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class LHHWKinetics:
    params: Dict

    def rate(self, P: Dict[str, float], T: float) -> float:
        A = self.params.get('A', 1e6)
        Ea = self.params.get('Ea', 80000.0)
        k = A * np.exp(-Ea / (8.314 * T))
        num = P.get('CO', 0.05) * P.get('O2', 0.21)
        den = 1.0 + 100.0 * P.get('CO', 0.05)
        return float(k * num / (den**2))


@dataclass
class EleyRidealKinetics:
    params: Dict

    def rate(self, P: Dict[str, float], T: float) -> float:
        k = self.params.get('A', 1e5) * np.exp(-self.params.get('Ea', 60000.0) / (8.314 * T))
        return float(k * P.get('CO', 0.05) * P.get('O2', 0.21) / (1.0 + 10.0 * P.get('CO', 0.05)))


@dataclass
class MarsVanKrevelenKinetics:
    params: Dict

    def rate(self, P: Dict[str, float], T: float) -> float:
        k1 = 1e4 * np.exp(-50000.0 / (8.314 * T))
        k2 = 1e5 * np.exp(-40000.0 / (8.314 * T))
        p_co = P.get('CO', 0.05)
        p_o2 = P.get('O2', 0.21)
        return float(k1 * k2 * p_co * p_o2 / (k2 * p_o2 + k1 * p_co + 1e-10))


@dataclass
class PowerLawKinetics:
    params: Dict

    def rate(self, P: Dict[str, float], T: float) -> float:
        k = self.params.get('A', 1e4) * np.exp(-self.params.get('Ea', 50000.0) / (8.314 * T))
        return float(k * (P.get('CO', 0.05)**1.0))
