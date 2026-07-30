"""
Periodic Boundary Conditions & Minimum Image Convention
"""
import numpy as np

def minimum_image_distance(pos1: np.ndarray, pos2: np.ndarray, box: np.ndarray) -> np.ndarray:
    dr = pos1 - pos2
    if box is not None:
        for dim in range(3):
            L = box[dim, dim]
            if L > 0:
                dr[dim] -= L * np.round(dr[dim] / L)
    return dr
