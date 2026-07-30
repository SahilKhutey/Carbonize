"""
Analysis of Experimental Designs (ANOVA & Regression)
"""
import numpy as np
from typing import Dict, List
from scipy.stats import f as f_dist


class ANOVA:
    def __init__(self, X: np.ndarray, y: np.ndarray, factor_names: List[str]):
        self.X = X
        self.y = y
        self.factor_names = factor_names
        self.k = X.shape[1]
        self.n = len(X)

    def main_effects(self) -> Dict:
        effects = {}
        for j in range(self.k):
            high_mask = self.X[:, j] >= 0.0
            low_mask = self.X[:, j] < 0.0
            high_mean = np.mean(self.y[high_mask]) if np.any(high_mask) else 0.0
            low_mean = np.mean(self.y[low_mask]) if np.any(low_mask) else 0.0
            effects[self.factor_names[j]] = float(high_mean - low_mean)
        return effects

    def anova_table(self) -> Dict:
        SS_total = np.sum((self.y - np.mean(self.y)) ** 2)
        df_total = self.n - 1
        X_design = np.column_stack([np.ones(self.n), self.X])
        beta = np.linalg.lstsq(X_design, self.y, rcond=None)[0]
        y_pred = X_design @ beta
        SS_model = np.sum((y_pred - np.mean(self.y)) ** 2)
        df_model = X_design.shape[1] - 1
        SS_residual = max(0.0, SS_total - SS_model)
        df_residual = max(1, df_total - df_model)
        MS_model = SS_model / max(1, df_model)
        MS_residual = SS_residual / df_residual
        F = MS_model / max(1e-10, MS_residual)
        R2 = SS_model / max(1e-10, SS_total)
        return {
            'SS_total': float(SS_total),
            'SS_model': float(SS_model),
            'SS_residual': float(SS_residual),
            'F_statistic': float(F),
            'R_squared': float(R2),
        }


class RegressionModel:
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = np.column_stack([np.ones(len(X)), X])
        self.y = y
        self.beta = np.linalg.lstsq(self.X, self.y, rcond=None)[0]

    def predict(self, X_new: np.ndarray) -> np.ndarray:
        X_full = np.column_stack([np.ones(len(X_new)), X_new])
        return X_full @ self.beta
