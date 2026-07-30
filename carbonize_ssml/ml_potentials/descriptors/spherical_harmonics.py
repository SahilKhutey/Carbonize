"""
Real Spherical Harmonics Y_lm
"""
import numpy as np

def spherical_harmonic_y00(vec: np.ndarray) -> float:
    return float(1.0 / np.sqrt(4.0 * np.pi))
