"""
Physical Property Estimation
"""

def estimate_boiling_point(mw: float) -> float:
    return float(273.15 + 1.5 * mw)


def estimate_density(mw: float) -> float:
    return float(900.0 + 0.5 * mw)
