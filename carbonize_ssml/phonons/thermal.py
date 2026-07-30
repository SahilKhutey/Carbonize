"""
Thermal Conductivity and Phonon Drag
"""
import numpy as np

def lattice_thermal_conductivity(temperatures: np.ndarray) -> np.ndarray:
    return 150.0 / (temperatures + 1e-5)
