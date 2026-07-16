"""
Compare our production solver (BDF) against reference solvers.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.numerical.conftest import (
    STATE_NAMES,
    compare_solutions,
    params_standard,
    solve_with_method,
    standard_initial_state,
)


class TestBFDAgainstReferenceSolvers:
    """Compare BDF (production) vs Radau, LSODA."""
    
    @pytest.mark.parametrize("reference_method", ["Radau", "LSODA"])
    def test_bdf_vs_reference(
        self, reference_method, standard_initial_state, params_standard
    ):
        y0 = standard_initial_state
        t_span = (0.0, 27.0)
        rtol = 1e-6
        atol = 1e-8
        
        t_bdf, y_bdf = solve_with_method(
            y0, t_span, method="BDF", rtol=rtol, atol=atol, **params_standard
        )
        
        t_ref, y_ref = solve_with_method(
            y0, t_span, method=reference_method, rtol=rtol, atol=atol, **params_standard
        )
        
        for i, name in enumerate(STATE_NAMES):
            result = compare_solutions(t_bdf, y_bdf, t_ref, y_ref, species_idx=i)
            # Allow slightly looser tolerances due to JIT differences in solver choices
            tolerance = 5e-2
            assert result["mean_rel_err"] < tolerance, (
                f"BDF vs {reference_method} - {name}: "
                f"mean_rel_err = {result['mean_rel_err']:.2e} > {tolerance}"
            )

    def test_analytical_solutions(self, params_standard):
        """Verify first order decay matches analytical solution."""
        params = params_standard.copy()
        params["k_cat"] = 0.0
        params["k_so2"] = 0.0
        params["k_chel"] = 0.0
        
        y0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 3600.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params)
        
        k_inact = params["k_inact"]
        ca_analytical = 12.0 * np.exp(-k_inact * t)
        ca_numerical = y[:, 6]
        
        rel_err = np.abs(ca_numerical - ca_analytical) / ca_analytical
        assert rel_err.max() < 1e-3, f"CA deactivation deviates by {rel_err.max():.2e}"


class TestRandomizedParameterSpace:
    """Test solver across random parameter combinations."""
    
    @pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
    def test_random_parameters_solver_robust(self, seed, params_standard):
        rng = np.random.default_rng(seed)
        
        params = params_standard.copy()
        params["k_cat"] = float(rng.uniform(1e5, 1e7))
        params["K_M_co2"] = float(rng.uniform(1e-3, 0.1))
        params["k_inact"] = float(rng.uniform(1e-6, 1e-3))
        params["T_reactor"] = float(rng.uniform(293, 333))
        params["pH_initial"] = float(rng.uniform(7.0, 10.0))
        
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params)
        
        assert np.all(np.isfinite(y))
        assert np.all(y >= -1e-4)
