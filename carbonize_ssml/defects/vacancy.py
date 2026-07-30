"""
Vacancy Defect Formation Energy
"""
import numpy as np

def vacancy_formation_energy(E_defective: float, E_perfect: float, mu_removed: float) -> float:
    return float(E_defective - E_perfect + mu_removed)
