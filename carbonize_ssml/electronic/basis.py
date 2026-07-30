"""
PAW and Pseudopotential Library
"""
from typing import Dict, List

def get_pseudopotentials() -> List[Dict]:
    return [
        {'element': 'Si', 'type': 'PAW', 'cutoff_ry': 50.0},
        {'element': 'C', 'type': 'Norm-Conserving', 'cutoff_ry': 60.0},
        {'element': 'Fe', 'type': 'Ultrasoft', 'cutoff_ry': 45.0},
    ]
