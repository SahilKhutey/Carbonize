"""
Amorphous Polymer & Glass Transition Temperature
"""
from typing import Dict

def glass_transition_temperature(mw: float) -> float:
    return float(350.0 - 1000.0 / max(mw, 10.0))
