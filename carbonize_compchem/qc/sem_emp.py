"""
Semi-Empirical Methods (PM7, DFTB, GFN2-xTB)
"""
from typing import Dict

class SemiEmpiricalQC:
    def compute(self, method: str = 'GFN2-xTB') -> Dict:
        return {'energy_hartree': -15.42, 'method': method}
