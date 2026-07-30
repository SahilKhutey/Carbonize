"""
ZT Figure of Merit
"""
def compute_zt(S: float, sigma: float, T: float, kappa: float) -> float:
    return float(S**2 * sigma * T / max(kappa, 1e-5))
