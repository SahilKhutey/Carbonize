"""
Electrical and Thermal Conductivity
"""
import numpy as np

def electrical_conductivity(n: float, mobility: float) -> float:
    return float(n * 1.602e-19 * mobility)
