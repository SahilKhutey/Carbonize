"""
Basis Set Library (STO-3G, 6-31G*, cc-pVTZ)
"""
from typing import Dict, List

def get_basis_library() -> List[Dict]:
    return [
        {'name': 'sto-3g', 'size': 'minimal'},
        {'name': '6-31g*', 'size': 'polarized'},
        {'name': 'cc-pvtz', 'size': 'triple-zeta'},
    ]
