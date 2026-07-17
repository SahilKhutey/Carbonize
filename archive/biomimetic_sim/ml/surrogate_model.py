"""
ml/surrogate_model.py
Fits a Gaussian Process surrogate model over the stiff kinetics ODE solver.
Provides extremely fast approximations for flowsheet optimization.
"""

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from core.kinetics import solve_reactor_kinetics

class KineticsSurrogateModel:
    """
    Surrogate Gaussian Process model to approximate CO2/SO2 capture efficiencies.
    """
    def __init__(self):
        # Matern 5/2 kernel with bounds to capture non-linear relationships
        kernel = 1.0 * Matern(length_scale=[10.0, 1.0, 100.0], nu=2.5)
        self.gp_co2 = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
        self.gp_so2 = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
        self.fitted = False

    def generate_training_data(self, samples: int = 50):
        """
        Samples the real ODE solver to generate a training dataset.
        """
        X = []
        y_co2 = []
        y_so2 = []

        for _ in range(samples):
            # Uniformly sample inputs within operational boundaries
            enzyme = np.random.uniform(1.0, 50.0)      # mg/L
            temp = np.random.uniform(20.0, 60.0)       # C
            flow = np.random.uniform(1000.0, 15000.0)  # Nm3/hr

            X.append([enzyme, temp, flow])

            # Run physical BDF ODE solver
            res = solve_reactor_kinetics(
                co2_vol_pct=14.0,
                so2_mg_per_nm3=1200.0,
                flow_nm3_per_hr=flow,
                enzyme_mg_per_l=enzyme,
                calcium_source_g_per_l=35.0,
                reactor_temp_c=temp
            )
            y_co2.append(res["co2_capture_efficiency_pct"])
            y_so2.append(res["so2_capture_efficiency_pct"])

        return np.array(X), np.array(y_co2), np.array(y_so2)

    def fit(self, samples: int = 50):
        """
        Fits the GP Regressor models.
        """
        X, y_co2, y_so2 = self.generate_training_data(samples)
        self.gp_co2.fit(X, y_co2)
        self.gp_so2.fit(X, y_so2)
        self.fitted = True

    def predict_capture(self, enzyme: float, temp: float, flow: float):
        """
        Returns fast predictions along with standard deviation (uncertainty).
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before predicting.")

        X_new = np.array([[enzyme, temp, flow]])
        mu_co2, std_co2 = self.gp_co2.predict(X_new, return_std=True)
        mu_so2, std_so2 = self.gp_so2.predict(X_new, return_std=True)

        return {
            "co2_capture_efficiency_pct": max(0.0, min(100.0, float(mu_co2[0]))),
            "co2_uncertainty_pct": float(std_co2[0]),
            "so2_capture_efficiency_pct": max(0.0, min(100.0, float(mu_so2[0]))),
            "so2_uncertainty_pct": float(std_so2[0])
        }
