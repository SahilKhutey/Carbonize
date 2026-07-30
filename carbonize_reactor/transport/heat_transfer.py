"""
Heat transfer correlations
"""

def external_heat_transfer(Re: float, Pr: float) -> float:
    return float(2.0 + 0.6 * (Re**0.5) * (Pr**(1.0/3.0)))
