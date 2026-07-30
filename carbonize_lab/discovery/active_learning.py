"""
Active Learning Sample Selection
"""
import numpy as np
from typing import Dict, List

class ActiveLearner:
    def select_candidates(self, pool: List[Dict], n_select: int = 5) -> List[Dict]:
        return pool[:n_select]
