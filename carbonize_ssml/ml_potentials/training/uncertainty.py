"""
Ensemble Uncertainty Quantifier
"""
import numpy as np
from typing import List, Dict

class CommitteeUncertainty:
    def __init__(self, models: List):
        self.models = models

    def predict_with_uncertainty(self, structure) -> Dict:
        preds = [float(m.forward(structure.positions, structure.elements)) for m in self.models]
        return {
            'mean': float(np.mean(preds)),
            'std': float(np.std(preds)),
            'max_abs_dev': float(np.max(np.abs(np.array(preds) - np.mean(preds)))),
            'individual_predictions': preds,
        }
