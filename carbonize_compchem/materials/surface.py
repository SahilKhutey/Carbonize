"""
Surface Slab Model Builder & Surface Energy
"""
import numpy as np
from typing import Dict

def surface_energy(E_slab: float, E_bulk_per_atom: float, n_atoms: int, area: float) -> float:
    return float((E_slab - n_atoms * E_bulk_per_atom) / (2.0 * max(area, 1e-5)))
