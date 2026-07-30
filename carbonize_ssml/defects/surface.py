"""
Surface Energy & Relaxation
"""
def surface_energy(E_slab: float, E_bulk: float, area: float) -> float:
    return float((E_slab - E_bulk) / (2.0 * max(area, 1e-5)))
