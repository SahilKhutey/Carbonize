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
    CO2 hydration term, expressed in natural bench assay units (mM, U/mL).

    Note on enzyme concentration scaling: CA_U_per_mL is specified in U/mL
    (where 1 U = 1.6667e-8 mol/s activity scale). E_molar (mol/L) = CA_U_per_mL * 1.6667e-8.

    Returns predicted rate in mol/(L*s), matching CE-1's rate_mol_per_L_s observation column.
    """
    k_cat_T = k_cat * np.exp(-E_a / R_GAS * (1.0 / T_K - 1.0 / T_REF_K))
    pH_factor = np.where(pH < 7.0, 10 ** (pH - 7.0), 1.0)
    E_molar = CA_U_per_mL * 1.6667e-8
    rate = (k_cat_T * E_molar * CO2_mM) / (K_M * (1.0 + HCO3_mM / K_i) + CO2_mM)
    return rate * pH_factor


def ca_rate_residuals(params, X, y_obs):
    """Residual function for least_squares fitting against ca_rate_model."""
    T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM = X
    k_cat, K_M, K_i, E_a = params
    y_pred = ca_rate_model(T_K, pH, CO2_mM, CA_U_per_mL, HCO3_mM, k_cat, K_M, K_i, E_a)
    return y_obs - y_pred


def caco3_precipitation_rate(
    Ca_mM: np.ndarray | float,
    HCO3_mM: np.ndarray | float,
    k_precip_caco3: float,
    chitosan_pct: np.ndarray | float = 1.0,
    pH: np.ndarray | float = 8.5,
    Ksp_caco3: float = 3.31e-9,
) -> np.ndarray | float:
    """
    CE-3: CaCO3 precipitation rate model driven by supersaturation ion product,
    chitosan crystallization template scaling, and pH carbonate speciation.

    rate = k_precip_caco3 * max(0, [Ca²⁺][HCO₃⁻] - Ksp_caco3) * chitosan_pct * 10^(pH - 8.5)

    Units:
      - Ca_mM, HCO3_mM in mM (= mol/m³)
      - Ksp_caco3 in mol²/m⁶ (default 3.31e-9)
      - k_precip_caco3 in m³/(mol·s)
      - Returns predicted precipitation rate in mol/(L·s), matching CE-3's
        rate_mol_per_L_s observation column.
    """
    ion_product = np.maximum(0.0, (Ca_mM * HCO3_mM) - Ksp_caco3)
    template_factor = np.maximum(0.1, np.asarray(chitosan_pct, dtype=float))
    pH_factor = 10.0 ** (np.asarray(pH, dtype=float) - 8.5)
    return k_precip_caco3 * ion_product * template_factor * pH_factor


def multi_gas_removal_efficiency(
    k_abs: float,
    residence_time_s: np.ndarray | float,
) -> np.ndarray | float:
    """
    CE-4: First-order gas-liquid absorption removal efficiency (%).

    efficiency_pct = (1.0 - exp(-k_abs * residence_time_s)) * 100.0

    Units:
      - k_abs in s⁻¹ (or m/s mass transfer velocity scale)
      - residence_time_s in seconds (derived from L_per_min flow rate)
      - Returns predicted gas removal efficiency in %, matching CE-4's
        resolved target column.
    """
    return (1.0 - np.exp(-k_abs * residence_time_s)) * 100.0


def formulation_strength_response(
    chitosan_pct: np.ndarray | float,
    pH: np.ndarray | float,
    strength_coeff_chitosan: float,
    pH_coeff_strength: float = 0.1,
) -> np.ndarray | float:
    """
    CE-5: Composite block compressive strength response (MPa) model.

    strength_mpa = strength_coeff_chitosan * chitosan_pct * (1.0 + pH_coeff_strength * max(0, pH - 7.0))

    Units:
      - chitosan_pct in wt% (1.0 to 5.0%)
      - pH in pH units (7.0 to 10.0)
      - strength_coeff_chitosan in MPa/wt%
      - Returns predicted compressive strength in MPa, matching CE-5's response column.
    """
    pH_factor = 1.0 + pH_coeff_strength * np.maximum(0.0, pH - 7.0)
    return strength_coeff_chitosan * chitosan_pct * pH_factor


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
    "CE-3": {
        "predict": caco3_precipitation_rate,
        "observed_column": "rate_mol_per_L_s",
        "input_columns": ["Ca_mM", "HCO3_mM", "chitosan_pct", "pH"],
        "param_paths": ["kinetics.k_precip_caco3"],
    },
    "CE-4": {
        "predict": multi_gas_removal_efficiency,
        "observed_column": "removal_efficiency_pct",
        "input_columns": ["L_per_min"],
        "param_paths": ["kinetics.k_so2_abs", "kinetics.k_no2_abs"],
    },
    "CE-5": {
        "predict": formulation_strength_response,
        "observed_column": "response",
        "input_columns": ["chitosan_pct", "pH"],
        "param_paths": ["kinetics.strength_coeff_chitosan", "kinetics.pH_coeff_strength"],
    },
    # CE-2 (heavy metal Freundlich sorption) does not have a forward-prediction
    # model here yet. UQRunner raises a clear NotImplementedError for it.
}
