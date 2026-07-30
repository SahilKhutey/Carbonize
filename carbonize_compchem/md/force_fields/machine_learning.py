"""
Neural Network Force Fields (ANI/SchNet style ML potentials)
"""
import numpy as np

class NeuralNetworkPotential:
    def predict_forces(self, positions: np.ndarray) -> np.ndarray:
        return np.zeros_like(positions)
