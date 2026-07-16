"""
Pytest configuration and shared fixtures for numerical validation tests.
"""

from __future__ import annotations

from typing import Tuple
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.engine import KineticsEngine
from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba

# Reference parameter set (from v2026.1.json)
REFERENCE_PARAMS = {
    "k_cat": 1.0e6,
    "K_M_co2": 8.5e-3,
    "k_inact": 5.0e-5,
    "E_a_inact": 85.0e3,
    "k_so2": 2.5e-2,
    "k_chel": 8.0e-3,
    "ca_cl2": 0.5 * 1000.0 / 74.10,  # 0.5 M Ca²⁺
    "pH_initial": 8.5,
    "T_reactor": 40.0 + 273.15,
}

# State vector indices (9 species)
STATE_NAMES = [
    "CO2_aq", "HCO3", "Ca2", "CaCO3_s",
    "SO2_aq", "CaSO4_s", "CA_active", "Metal_chel", "PM_trapped"
]


def make_reference_rhs(method_params: dict):
    """
    Create a reference RHS function using our Numba kernel.
    """
    def rhs(t, y):
        return reaction_rhs_numba(
            t, y,
            k_cat=method_params["k_cat"],
            K_M_co2=method_params["K_M_co2"],
            k_inact=method_params["k_inact"],
            E_a_inact=method_params["E_a_inact"],
            k_so2=method_params["k_so2"],
            k_chel=method_params["k_chel"],
            ca_cl2=method_params["ca_cl2"],
            pH_initial=method_params["pH_initial"],
            T_reactor=method_params["T_reactor"],
        )
    return rhs


def solve_with_method(
    y0: np.ndarray,
    t_span: Tuple[float, float],
    method: str = "BDF",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    max_step: float = np.inf,
    **params,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve the ODE with specified method.
    """
    rhs = make_reference_rhs(params)
    
    sol = solve_ivp(
        fun=rhs,
        t_span=t_span,
        y0=y0,
        method=method,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        dense_output=True,
    )
    
    if not sol.success:
        raise RuntimeError(f"Solver {method} failed: {sol.message}")
    
    return sol.t, sol.y.T


@pytest.fixture(scope="module")
def kinetics_engine():
    """Kinetics engine with warmed-up Numba kernels."""
    engine = KineticsEngine()
    engine.warmup()
    return engine


@pytest.fixture
def standard_initial_state():
    """Initial state for standard conditions (mol/m³, except CA in mg/L)."""
    return np.array([
        10.0,    # [0] CO2_aq
        1.0,     # [1] HCO3⁻
        100.0,   # [2] Ca²⁺
        0.0,     # [3] CaCO3_s
        0.5,     # [4] SO2_aq
        0.0,     # [5] CaSO4_s
        12.0,    # [6] CA_active
        0.0,     # [7] Metal_chelated
        0.0,     # [8] PM_trapped
    ])


@pytest.fixture
def params_standard():
    """Standard operating parameters."""
    return REFERENCE_PARAMS.copy()


@pytest.fixture
def params_extreme_hot():
    """Extreme high temperature (70°C) — stiff system."""
    p = REFERENCE_PARAMS.copy()
    p["T_reactor"] = 70.0 + 273.15
    p["pH_initial"] = 7.0
    return p


@pytest.fixture
def params_extreme_cold():
    """Extreme low temperature (10°C) — slow dynamics."""
    p = REFERENCE_PARAMS.copy()
    p["T_reactor"] = 10.0 + 273.15
    p["pH_initial"] = 9.5
    return p


@pytest.fixture
def params_extreme_ph_acidic():
    """Extreme acidic pH (5.0) — CA activity severely reduced."""
    p = REFERENCE_PARAMS.copy()
    p["pH_initial"] = 5.0
    return p


@pytest.fixture
def params_extreme_ph_basic():
    """Extreme basic pH (11.0)."""
    p = REFERENCE_PARAMS.copy()
    p["pH_initial"] = 11.0
    return p


@pytest.fixture
def params_high_so2():
    """High SO₂ concentration (3000 mg/Nm³)."""
    p = REFERENCE_PARAMS.copy()
    p["k_so2"] = 5.0e-2
    return p


@pytest.fixture
def params_near_zero_concentrations():
    """Very dilute system (near-zero concentrations)."""
    return REFERENCE_PARAMS.copy()


def relative_error(y1: np.ndarray, y2: np.ndarray, eps: float = 1e-2) -> np.ndarray:
    """
    Compute relative error between two solutions.
    
    Uses eps as a hybrid absolute/relative tolerance floor for denom.
    """
    y1 = np.atleast_2d(y1)
    y2 = np.atleast_2d(y2)
    abs_err = np.abs(y1 - y2)
    denom = np.maximum(np.abs(y1), np.abs(y2))
    return abs_err / np.maximum(denom, eps)


def compare_solutions(
    t1: np.ndarray, y1: np.ndarray,
    t2: np.ndarray, y2: np.ndarray,
    species_idx: int = 0,
) -> dict:
    """
    Compare two solutions at matching time points (by interpolation).
    """
    from scipy.interpolate import interp1d
    
    interp_func = interp1d(t2, y2[:, species_idx], kind='linear', 
                           bounds_error=False, fill_value='extrapolate')
    y2_interp = interp_func(t1)
    
    y1_species = y1[:, species_idx]
    
    abs_err = np.abs(y1_species - y2_interp)
    rel_err = relative_error(y1_species, y2_interp)
    
    return {
        "max_rel_err": float(np.nanmax(rel_err)),
        "mean_rel_err": float(np.nanmean(rel_err)),
        "max_abs_err": float(np.nanmax(abs_err)),
        "time_series_rel_err": rel_err,
        "time_series_abs_err": abs_err,
    }
