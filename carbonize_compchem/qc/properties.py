"""
Electronic Property Calculations (HOMO-LUMO Gap, Dipole)
"""
from typing import Dict

def electronic_properties(E_homo: float = -0.32, E_lumo: float = -0.05) -> Dict:
    return {
        'homo_ev': float(E_homo * 27.2114),
        'lumo_ev': float(E_lumo * 27.2114),
        'band_gap_ev': float((E_lumo - E_homo) * 27.2114),
    }
