"""
Combined Energy and Force Loss
"""
import numpy as np

def compute_loss(pred_E: float, target_E: float, pred_F: np.ndarray, target_F: np.ndarray, w_force: float = 10.0) -> float:
    return float((pred_E - target_E)**2 + w_force * np.mean((pred_F - target_F)**2))
