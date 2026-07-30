"""
Defect Formation Energy & Dopant Analysis
"""
from typing import Dict

def defect_formation_energy(E_defect: float, E_bulk: float, mu_removed: float) -> float:
    return float(E_defect - E_bulk + mu_removed)
