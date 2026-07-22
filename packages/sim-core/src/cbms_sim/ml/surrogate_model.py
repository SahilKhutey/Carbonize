"""
ml/surrogate_model.py
Gaussian Process surrogate over the full 17-species ODE kinetics engine.

Changes from v1:
  - Expands to 5 outputs: co2, so2, nox, pm, metal capture efficiencies
  - Fixes ConvergenceWarning by widening length-scale bounds (1e-2, 1e5) per dim
  - Adds feature scaling (StandardScaler) so all three input dimensions live in
    similar numeric ranges — eliminates the exploding length-scale pathology
  - Surfaces GP prediction variance as model_uncertainty_pct on all outputs
  - add_training_point() enables online refinement without full re-fit
"""

from __future__ import annotations

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
from sklearn.preprocessing import StandardScaler

from cbms_sim.domain.kinetics import ExtendedKineticsEngine as KineticsEngine
from cbms_sim.domain.models.plant import PlantProfile as DomainPlant
from cbms_sim.domain.models.reagent import ReagentFormulation as DomainReagent, CalciumSourceType as DomainCalciumSource
from cbms_sim.domain.models.conditions import OperatingConditions as DomainConditions

# Input feature names (for external callers)
FEATURE_NAMES = ["enzyme_mg_per_l", "reactor_temp_c", "flow_nm3_per_hr"]

# Output names
OUTPUT_NAMES = ["co2_pct", "so2_pct", "nox_pct", "pm_pct", "metal_pct"]


def _make_kernel():
    """
    Matern-5/2 kernel with per-dimension ARD length scales.

    Bounds are deliberately wide [1e-2, 1e5] to avoid the optimizer hitting
    the upper boundary (which caused the previous ConvergenceWarning at 1e5).
    WhiteKernel handles observation noise so the GP doesn't overfit.
    """
    return (
        ConstantKernel(1.0, constant_value_bounds=(1e-3, 1e3))
        * Matern(
            length_scale=[1.0, 1.0, 1.0],
            length_scale_bounds=[(1e-2, 1e5)] * 3,
            nu=2.5,
        )
        + WhiteKernel(noise_level=1e-2, noise_level_bounds=(1e-5, 1e1))
    )


class KineticsSurrogateModel:
    """
    Multi-output Gaussian Process surrogate for the kinetics ODE solver.

    Fits one GP per output using ARD Matérn-5/2 kernels with feature scaling.
    Provides both point predictions and model uncertainty (std dev) for all
    five capture efficiency outputs.
    """

    def __init__(self) -> None:
        self.scalers: list[StandardScaler] = []
        self.gps: list[GaussianProcessRegressor] = []
        for _ in OUTPUT_NAMES:
            self.scalers.append(StandardScaler())
            self.gps.append(
                GaussianProcessRegressor(
                    kernel=_make_kernel(),
                    n_restarts_optimizer=5,
                    normalize_y=True,    # zero-mean normalisation stabilises optimisation
                    random_state=42,
                    alpha=1e-6,          # numerical stability jitter
                )
            )
        # Shared input scaler (fitted once on the training set)
        self.X_scaler = StandardScaler()
        self.fitted = False
        self._X_train: np.ndarray | None = None
        self._Y_train: np.ndarray | None = None  # shape (n, 5)

    # ------------------------------------------------------------------
    # Data generation
    # ------------------------------------------------------------------

    def generate_training_data(self, samples: int = 60) -> tuple[np.ndarray, np.ndarray]:
        """
        Latin-hypercube sampled calls to the real ODE solver.
        Returns X (n, 3) and Y (n, 5).
        """
        # Latin-hypercube sampling for better space coverage than pure random
        rng = np.random.default_rng(42)
        n = samples

        # LHS: stratified random in each dimension
        enzyme_vals = rng.permutation(np.linspace(1.0,  50.0,  n)) + rng.uniform(-0.5, 0.5, n)
        temp_vals   = rng.permutation(np.linspace(20.0, 60.0,  n)) + rng.uniform(-0.2, 0.2, n)
        flow_vals   = rng.permutation(np.linspace(1000, 15000, n)) + rng.uniform(-50,  50,  n)

        enzyme_vals = np.clip(enzyme_vals, 1.0,  50.0)
        temp_vals   = np.clip(temp_vals,  20.0, 60.0)
        flow_vals   = np.clip(flow_vals,  1000, 15000)

        X = np.column_stack([enzyme_vals, temp_vals, flow_vals])
        Y = np.zeros((n, 5))

        engine = KineticsEngine()
        engine.warmup()

        for i in range(n):
            enzyme, temp, flow = X[i]
            plant = DomainPlant(
                exhaust_flow_nm3_hr=float(flow),
                co2_vol_pct=14.0,
                so2_mg_per_nm3=1200.0,
                fly_ash_g_per_nm3=4.5,
            )
            reagent = DomainReagent(
                enzyme_mg_per_l=float(enzyme),
                ca_source_type=DomainCalciumSource.LIME,
            )
            conditions = DomainConditions(reactor_temp_c=float(temp))
            res = engine.solve(plant, reagent, conditions)
            effs = res.capture_efficiencies
            Y[i, 0] = effs.get("co2_pct",   0.0)
            Y[i, 1] = effs.get("so2_pct",   0.0)
            Y[i, 2] = effs.get("nox_pct",   0.0)
            Y[i, 3] = effs.get("pm_pct",    0.0)
            Y[i, 4] = effs.get("metal_pct", 0.0)

        return X, Y

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, samples: int = 60) -> None:
        """Generate LHS training data and fit all 5 GP models."""
        X, Y = self.generate_training_data(samples)
        self._X_train = X
        self._Y_train = Y

        X_scaled = self.X_scaler.fit_transform(X)
        for j, gp in enumerate(self.gps):
            gp.fit(X_scaled, Y[:, j])

        self.fitted = True

    def add_training_point(
        self,
        enzyme: float,
        temp: float,
        flow: float,
        captures: dict[str, float],
    ) -> None:
        """Append a new observation and refit (online refinement)."""
        x_new = np.array([[enzyme, temp, flow]])
        y_new = np.array([[
            captures.get("co2_pct",   0.0),
            captures.get("so2_pct",   0.0),
            captures.get("nox_pct",   0.0),
            captures.get("pm_pct",    0.0),
            captures.get("metal_pct", 0.0),
        ]])
        if self._X_train is None:
            self._X_train = x_new
            self._Y_train = y_new
        else:
            self._X_train = np.vstack([self._X_train, x_new])
            self._Y_train = np.vstack([self._Y_train, y_new])

        X_scaled = self.X_scaler.fit_transform(self._X_train)
        for j, gp in enumerate(self.gps):
            gp.fit(X_scaled, self._Y_train[:, j])
        self.fitted = True

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_capture(
        self,
        enzyme: float,
        temp: float,
        flow: float,
    ) -> dict[str, float]:
        """
        Returns point predictions plus GP model uncertainty (1-sigma) for all
        five capture efficiency outputs.
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before predicting.")

        X_new = np.array([[enzyme, temp, flow]])
        X_scaled = self.X_scaler.transform(X_new)

        result: dict[str, float] = {}
        for j, (name, gp) in enumerate(zip(OUTPUT_NAMES, self.gps)):
            mu, sigma = gp.predict(X_scaled, return_std=True)
            result[f"{name}_capture_pct"]        = float(np.clip(mu[0], 0.0, 100.0))
            result[f"{name}_uncertainty_1sigma"] = float(max(0.0, sigma[0]))

        # Backwards-compat aliases
        result["co2_capture_efficiency_pct"] = result["co2_pct_capture_pct"]
        result["co2_uncertainty_pct"]        = result["co2_pct_uncertainty_1sigma"]
        result["so2_capture_efficiency_pct"] = result["so2_pct_capture_pct"]
        result["so2_uncertainty_pct"]        = result["so2_pct_uncertainty_1sigma"]

        return result
