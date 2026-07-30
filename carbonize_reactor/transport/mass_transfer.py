"""
External mass transfer correlations
"""
import numpy as np


def external_mass_transfer(Re: float, Sc: float) -> float:
    return float(2.0 + 0.6 * (Re**0.5) * (Sc**(1.0/3.0)))
