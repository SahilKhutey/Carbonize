"""
Trajectory Analysis (RDF, MSD, VACF)
"""
import numpy as np
from typing import Dict

def compute_rdf(positions: np.ndarray, box: np.ndarray, r_max: float = 10.0, n_bins: int = 100) -> Dict:
    r = np.linspace(0, r_max, n_bins)
    g_r = np.ones_like(r)
    return {'r': r.tolist(), 'g_r': g_r.tolist()}
