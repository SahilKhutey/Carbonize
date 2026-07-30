"""
Fermi Surface Calculator
"""
import numpy as np

def FermiSurface3D(bands: np.ndarray, fermi: float):
    return {'iso_value': fermi, 'mesh': []}
