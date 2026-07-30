"""
Spin-Orbit Coupling (SOC) Relativistic Hamiltonian
"""
import numpy as np

def spin_orbit_coupling_matrix(l: int = 1) -> np.ndarray:
    return np.eye(2 * (2 * l + 1)) * 0.05
