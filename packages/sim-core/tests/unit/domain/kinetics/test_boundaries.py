"""Boundary condition tests: edge cases and degenerate inputs."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba


class TestZeroBoundaryConditions:
    """All concentrations zero - system should be quiescent."""
    
    def test_zero_state_does_not_explode(self, standard_params):
        y0 = np.zeros(9)
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 100), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        assert sol.success
        assert np.all(np.isfinite(sol.y))
        assert np.all(sol.y >= -1e-3)
    
    def test_partial_zero_state(self, standard_params):
        """Only Ca and CA present, no acid gases."""
        # Disable SO2 absorption so Ca doesn't react with newly absorbed SO2
        params = standard_params.copy()
        params["k_so2"] = 0.0
        
        y0 = np.array([0, 0, 100.0, 0, 0, 0, 12.0, 0, 0])
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            (0, 100), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        assert sol.success
        # Ca should stay 100 (no reaction), CA decays
        np.testing.assert_allclose(sol.y[2, -1], 100.0, rtol=1e-6)
        assert sol.y[6, -1] < 12.0


class TestSaturationBoundary:
    """At equilibrium, rates should approach zero."""
    
    def test_high_co2_equilibrium(self, standard_params):
        """High CO2 -> bicarbonate formation, then equilibrium."""
        y0 = np.array([1000.0, 0.0, 100.0, 0.0, 0.0, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 1000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        assert sol.success
        # All concentrations except cumulative PM trapped should remain bounded
        assert np.all(sol.y[:-1, -1] < 2000)


class TestNumericalStability:
    """Solutions should not contain NaN or Inf under normal conditions."""
    
    @pytest.mark.parametrize("seed", range(10))
    def test_random_initial_states_stable(self, seed, standard_params):
        """Random non-negative initial states should solve cleanly."""
        rng = np.random.default_rng(seed)
        y0 = rng.uniform(0, 100, 9)
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 100), y0, method="BDF", rtol=1e-6, atol=1e-9
        )
        
        assert sol.success, f"Solver failed for seed {seed}"
        assert np.all(np.isfinite(sol.y)), f"NaN/Inf for seed {seed}"
        assert np.all(sol.y >= -1e-3), f"Negative concentrations for seed {seed}"
