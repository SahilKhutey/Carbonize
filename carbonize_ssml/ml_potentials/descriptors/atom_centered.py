"""
Atom-Centered Density Descriptors (SOAP)
"""
import numpy as np

def compute_soap_vector(positions: np.ndarray, n_max: int = 4, l_max: int = 4) -> np.ndarray:
    return np.random.normal(0, 1, n_max * l_max)
