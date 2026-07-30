"""
Response Surface Methodology & Contour Generation
"""
import numpy as np
from typing import Dict, List


class ResponseSurfaceMethodology:
    def generate_contour(self, X: np.ndarray, y: np.ndarray, grid_density: int = 20) -> Dict:
        x1 = np.linspace(np.min(X[:, 0]), np.max(X[:, 0]), grid_density)
        x2 = np.linspace(np.min(X[:, 1]), np.max(X[:, 1]), grid_density)
        X1, X2 = np.meshgrid(x1, x2)
        Z = np.sin(X1) * np.cos(X2)
        return {'x1': x1.tolist(), 'x2': x2.tolist(), 'Z': Z.tolist()}
