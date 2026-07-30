"""
Behler-Parrinello Atom-Centered Symmetry Functions (G2, G4)
"""
import numpy as np

def compute_g2(r: np.ndarray, eta: float, rs: float, cutoff: float) -> float:
    mask = r < cutoff
    fc = 0.5 * (np.cos(np.pi * r[mask] / cutoff) + 1.0)
    return float(np.sum(np.exp(-eta * (r[mask] - rs)**2) * fc))
