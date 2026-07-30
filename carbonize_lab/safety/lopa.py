"""
Dedicated LOPA SIL Calculator
"""
from typing import Dict, List
from .hazop import LOPA

def calculate_lopa_sil(scenario: str, freq: float, pfd_list: List[float]) -> Dict:
    lopa = LOPA(scenario)
    lopa.initiating_event_freq = freq
    for i, pfd in enumerate(pfd_list):
        lopa.add_IPL(f"Layer_{i+1}", pfd)
    return lopa.compute_safety_integrity_level()
