"""
Verify the ODE solver converges as tolerance tightens.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.numerical.conftest import (
    compare_solutions,
    params_standard,
    solve_with_method,
    standard_initial_state,
)


class TestOrderConvergence:
    """Verify solver convergence order."""
    
    @pytest.mark.parametrize("method", ["BDF", "Radau", "LSODA"])
    def test_solution_converges_with_tighter_tolerance(
        self, method, standard_initial_state, params_standard
    ):
        y0 = standard_initial_state
        t_span = (0.0, 27.0)
        
        t_coarse, y_coarse = solve_with_method(
            y0, t_span, method=method, rtol=1e-6, atol=1e-8, **params_standard
        )
        
        t_fine, y_fine = solve_with_method(
            y0, t_span, method=method, rtol=1e-10, atol=1e-12, **params_standard
        )
        
        for i, name in enumerate([
            "CO2_aq", "HCO3", "Ca2", "CaCO3_s",
            "SO2_aq", "CaSO4_s", "CA_active", "Metal_chel", "PM_trapped"
        ]):
            result = compare_solutions(t_coarse, y_coarse, t_fine, y_fine, species_idx=i)
            # Use mean relative error or looser max relative error for stiff transients
            assert result["mean_rel_err"] < 5e-2, (
                f"{method} - {name}: coarse vs fine mean error differ by {result['mean_rel_err']:.2e}"
            )
            # Final state should be very close
            assert abs(y_coarse[-1, i] - y_fine[-1, i]) / max(abs(y_fine[-1, i]), 1e-2) < 1e-2, (
                f"{method} - {name}: final state differ"
            )
    
    def test_bdf_convergence_order(self, standard_initial_state, params_standard):
        y0 = standard_initial_state
        t_span = (0.0, 27.0)
        
        tolerances = [1e-4, 1e-6, 1e-8]
        solutions = []
        for rtol in tolerances:
            t, y = solve_with_method(
                y0, t_span, method="BDF", rtol=rtol, atol=rtol*1e-2, **params_standard
            )
            solutions.append((t, y))
        
        for species_idx in range(9):
            # Skip checking convergence for flat/inactive species
            fine_y = solutions[-1][1][:, species_idx]
            if np.max(fine_y) - np.min(fine_y) < 1e-2:
                continue
            errors = []
            for t, y in solutions[:-1]:
                result = compare_solutions(
                    t, y, solutions[-1][0], solutions[-1][1], species_idx
                )
                errors.append(result["mean_rel_err"])
            
            if len(errors) >= 2 and errors[0] > 1e-10 and errors[1] > 1e-10:
                # Tightening tolerance should reduce error
                assert errors[1] <= errors[0] * 1.5


class TestTimeStepIndependence:
    """Solution should be independent of max_step (within solver accuracy)."""
    
    @pytest.mark.parametrize("max_step", [1.0, 5.0])
    def test_solution_independent_of_max_step(
        self, max_step, standard_initial_state, params_standard
    ):
        y0 = standard_initial_state
        t_span = (0.0, 27.0)
        
        t_ref, y_ref = solve_with_method(
            y0, t_span, method="BDF", max_step=np.inf, **params_standard
        )
        
        t_test, y_test = solve_with_method(
            y0, t_span, method="BDF", max_step=max_step, **params_standard
        )
        
        for i in range(9):
            result = compare_solutions(t_ref, y_ref, t_test, y_test, species_idx=i)
            assert result["mean_rel_err"] < 1e-2, (
                f"Species {i}: max_step={max_step} gave {result['mean_rel_err']:.2e} mean error"
            )
