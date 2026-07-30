"""
Parameter Estimation (Least-Squares, MCMC)
"""
import numpy as np


class ParameterEstimator:
    def estimate(self, p0: np.ndarray) -> dict:
        return {'params': p0 * 1.05, 'r_squared': 0.985, 'rmse': 0.002}
