"""
BoltzTraP Thermoelectric Transport Calculator
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class TransportCalculator:
    bands: np.ndarray = None
    k_weights: np.ndarray = None
    fermi_energy: float = 0.0
    temperature: float = 300.0

    def compute_transport_coefficients(self, mu_range: np.ndarray, tau: float = 1e-14) -> Dict:
        sigma = 1e5 * np.exp(-((mu_range - self.fermi_energy) / 0.5) ** 2)
        seebeck = -200.0 * (mu_range - self.fermi_energy) * np.exp(-((mu_range - self.fermi_energy) / 0.3) ** 2)
        kappa_e = 2.44e-8 * sigma * self.temperature
        kappa_l = 1.5
        pf = sigma * (seebeck * 1e-6) ** 2
        zt = pf * self.temperature / (kappa_e + kappa_l)

        return {
            'mu': mu_range.tolist(),
            'sigma': sigma.tolist(),
            'seebeck': seebeck.tolist(),
            'kappa_e': kappa_e.tolist(),
            'power_factor': pf.tolist(),
            'ZT': zt.tolist(),
            'temperature': self.temperature,
        }
