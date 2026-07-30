"""
Dopant Substitution Calculator
"""
def dopant_substitution_energy(E_doped: float, E_perfect: float, mu_dopant: float, mu_host: float) -> float:
    return float(E_doped - E_perfect - mu_dopant + mu_host)
