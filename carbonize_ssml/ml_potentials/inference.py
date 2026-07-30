"""
Fast Inference Engine for MLIPs
"""
import numpy as np

class FastInferenceEngine:
    def predict(self, model, positions: np.ndarray, elements: list):
        return model.forward(positions, elements)
