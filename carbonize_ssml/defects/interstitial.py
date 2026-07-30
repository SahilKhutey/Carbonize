"""
Interstitial Defect Calculator
"""
def interstitial_formation_energy(E_defective: float, E_perfect: float, mu_added: float) -> float:
    return float(E_defective - E_perfect - mu_added)
