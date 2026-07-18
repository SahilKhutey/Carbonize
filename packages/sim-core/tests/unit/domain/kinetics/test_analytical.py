"""Tests against known analytical solutions."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba


class TestEnzymeDeactivationAnalytical:
    """CA activity decays exponentially: CA(t) = CA_0 * exp(-k_inact * t)."""
    
    def test_exponential_decay_at_reference_temperature(self):
        """
        At T_ref (40°C), disable all reactions except deactivation.
        Solution should be exactly exponential.
        """
        params = dict(
            k_cat=0, K_M_co2=0, k_inact=5.0e-5, E_a_inact=85.0e3,
            k_so2=0, k_chel=0, ca_cl2=0, pH_initial=8.5, T_reactor=313.15,
        )
        
        y0 = np.array([0, 0, 0, 0, 0, 0, 100.0, 0, 0])
        t_span = (0, 5000)
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            t_span, y0, method="BDF", rtol=1e-10, atol=1e-12
        )
        
        ca_analytical = 100.0 * np.exp(-5.0e-5 * sol.t)
        ca_numerical = sol.y[6, :]
        
        rel_err = np.abs(ca_numerical - ca_analytical) / ca_analytical
        assert rel_err.max() < 1e-5
    
    def test_arrhenius_temperature_dependence(self):
        """At different temperatures, k_inact follows Arrhenius."""
        E_a = 85.0e3
        R = 8.314
        
        params_40 = dict(
            k_cat=0, K_M_co2=0, k_inact=5.0e-5, E_a_inact=E_a,
            k_so2=0, k_chel=0, ca_cl2=0, pH_initial=8.5, T_reactor=313.15,
        )
        y0 = np.array([0, 0, 0, 0, 0, 0, 100.0, 0, 0])
        sol_40 = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params_40),
            (0, 30000), y0, method="BDF", rtol=1e-10, atol=1e-12, dense_output=True
        )
        t_grid = np.linspace(0, 30000, 100000)
        t_half_40 = t_grid[np.argmin(np.abs(sol_40.sol(t_grid)[6] - 50.0))]
        
        params_50 = params_40.copy()
        params_50["T_reactor"] = 323.15
        sol_50 = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params_50),
            (0, 30000), y0, method="BDF", rtol=1e-10, atol=1e-12, dense_output=True
        )
        t_half_50 = t_grid[np.argmin(np.abs(sol_50.sol(t_grid)[6] - 50.0))]
        
        predicted_ratio = np.exp(E_a / R * (1/313.15 - 1/323.15))
        measured_ratio = t_half_40 / t_half_50
        
        rel_err = abs(measured_ratio - predicted_ratio) / predicted_ratio
        assert rel_err < 0.05


class TestMichaelisMentenAnalytical:
    """At steady state, v = V_max * [S] / (K_M + [S])."""
    
    def test_mm_steady_state_low_substrate(self):
        """At [S] << K_M, rate is approximately linear in [S]."""
        params = dict(
            k_cat=1e6, K_M_co2=8.5e-3, k_inact=0,
            E_a_inact=0, k_so2=0, k_chel=0, ca_cl2=0,
            pH_initial=8.5, T_reactor=313.15,
        )
        
        # Evaluate initial rate directly
        y0_low = np.array([0.0001, 0, 100, 0, 0, 0, 30000.0, 0, 0])
        rates = reaction_rhs_numba(0.0, y0_low, **params)
        rate_low = -rates[0]
        
        # [S] << K_M => v ≈ (k_cat * [CA] * [S]) / K_M
        # At pH 8.5, CA has no inhibition/deactivation
        rate_predicted_low = 1e6 * 1.0 * 0.0001 / 8.5
        
        rel_err = abs(rate_low - rate_predicted_low) / rate_predicted_low
        assert rel_err < 0.05
    
    def test_mm_steady_state_high_substrate(self):
        """At [S] >> K_M, rate is approximately V_max (saturated)."""
        params = dict(
            k_cat=1e6, K_M_co2=8.5e-3, k_inact=0,
            E_a_inact=0, k_so2=0, k_chel=0, ca_cl2=0,
            pH_initial=8.5, T_reactor=313.15,
        )
        
        y0_high = np.array([1000.0, 0, 100, 0, 0, 0, 30000.0, 0, 0])
        rates = reaction_rhs_numba(0.0, y0_high, **params)
        rate_high = -rates[0]
        
        # [S] >> K_M => v ≈ V_max = k_cat * [CA]
        rate_predicted_high = 1e6 * 1.0
        
        rel_err = abs(rate_high - rate_predicted_high) / rate_predicted_high
        assert rel_err < 0.05


class TestPrecipitationKsp:
    """At equilibrium, [Ca2+][CO3 2-] = Ksp."""
    
    def test_precipitation_stops_at_solubility(self):
        """When SI < 1, precipitation rate -> 0."""
        params = dict(
            k_cat=0, K_M_co2=0, k_inact=0, E_a_inact=0,
            k_so2=0, k_chel=0, ca_cl2=0,
            pH_initial=8.5, T_reactor=313.15,
        )
        y0 = np.array([0, 0, 1e-3, 0, 0, 0, 0, 0, 0])
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            (0, 100), y0, method="BDF", rtol=1e-10, atol=1e-12
        )
        assert sol.success
        np.testing.assert_allclose(sol.y[3, :], 0, atol=1e-15)
