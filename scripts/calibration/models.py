"""
Shared forward-prediction models for calibration experiments.

Single source of truth for each experiment's physics, used by both:
  - fitters.py (fits parameters against observations via least_squares)
  - uq_runner.py (forward-predicts at observed conditions using a
    calibrated -- or baseline -- parameter set, for comparison against
    those same observations)

Keeping exactly one implementation per experiment's rate law is
deliberate: this codebase has already hit real bugs from the same
chemistry being reimplemented in more than one place and silently
drifting apart (see: domain.kinetics.engine vs. domain.kinetics.core,
and the duplicated ca_rate_model/_residuals_ca that used to live in
fitters.py before this module existed). Add new experiment models here,
not inline in whichever script happens to need them first.
"""
from __future__ import annotations

import numpy as np

R_GAS = 8.314       # J/(mol*K)
T_REF_K = 298.15    # 25 C reference temperature


def ca_rate_model(
    T_K: np.ndarray,
    pH: np.ndarray,
    CO2_mM: np.ndarray,
    CA_U_per_mL: np.ndarray,
    HCO3_mM: np.ndarray,
    k_cat: float,
    K_M: float,
    K_i: float,
    E_a: float,
) -> np.ndarray:
    """
    CE-1: enzyme-catalysed CO2 hydration rate (Michaelis-Menten with
    competitive HCO3- product inhibition and Arrhenius temperature
    correction). Same functional form as domain/kinetics/kernels.py's
    CO2 hydration term, but expressed in the bench-assay's natural units
    (mM, U/mL) rather than the reactor engine's mol/m^3 state vector --
    these are legitimately different unit systems for a bench assay vs.
    a reactor simulation, not the same unit-inconsistency bug already
    fixed in the reactor kinetics engine.

    Returns predicted rate in mol/(L*s), matching CE-1's
    rate_mol_per_L_s observation column.
    """
    k_cat_T = k_cat * np.exp(-E_a / R_GAS * (1.0 / T_K - 1.0 / T_REF_K))
    pH_factor = np.where(pH < 7.0, 10 ** (pH - 7.0), 1.0)
    rate = (k_cat_T * CA_U_per_mL * CO2_mM) / (K_M * (1.0 + HCO3_mM / K_i) + CO2_mM)
    return rate * pH_factor


def ca_rate_residuals(params, X, y_obs):
    """Residual function for least_squares fitting against ca_rate_model."""
    T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM = X
    k_cat, K_M, K_i, E_a = params
    y_pred = ca_rate_model(T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM, k_cat, K_M, K_i, E_a)
    return y_obs - y_pred


# Maps each experiment to (required observation columns, in the exact
# order its forward-prediction function expects them) and the parameter
# names (dotted paths as stored in the parameter-set JSON) it needs.
# Used by uq_runner.py to know how to build X from an observations
# DataFrame generically, and to know which experiments actually have a
# real forward predictor implemented yet vs. which don't.
EXPERIMENT_MODELS = {
    "CE-1": {
        "predict": ca_rate_model,
        "observed_column": "rate_mol_per_L_s",
        "input_columns": ["temperature_C", "pH", "CO2_mM", "CA_U_per_mL", "HCO3_mM"],
        "param_paths": ["kinetics.k_cat", "kinetics.K_M_co2", "kinetics.K_i_hco3", "kinetics.E_a_inact"],
    },
    # CE-2 (heavy metal Freundlich sorption), CE-3 (precipitation rate),
    # CE-4 (multi-gas absorption), and CE-5 (formulation sensitivity)
    # do not have forward-prediction models here yet. UQRunner raises a
    # clear NotImplementedError for these rather than silently returning
    # a generic reactor-scenario prediction that doesn't correspond to
    # what those experiments actually measure -- see uq_runner.py.
}
