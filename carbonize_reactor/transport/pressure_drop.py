"""
Pressure drop correlations (Ergun, Larkins)
"""

def ergun_equation(Re: float, d_p: float, eps: float, rho: float, v_s: float, mu: float) -> float:
    t1 = 150.0 * mu * v_s / (d_p**2 + 1e-10) * ((1.0 - eps)**2 / (eps**3 + 1e-10))
    t2 = 1.75 * rho * (v_s**2) / (d_p + 1e-10) * ((1.0 - eps) / (eps**3 + 1e-10))
    return float(t1 + t2)
