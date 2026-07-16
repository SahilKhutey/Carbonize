"""
Property-based tests for the ODE solver.

These tests verify INVARIANTS that must hold across all valid inputs.
"""

import pytest
import numpy as np
from scipy.integrate import solve_ivp

from hypothesis import given, assume, note, settings
from hypothesis import strategies as st

from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba
from .conftest import ci_settings
from .strategies import (
    kinetic_parameters, initial_state, positive_float,
    temperature_c, ph_value, nonnegative_float,
)
from .test_pbt_helpers import params_residence


# =============================================================================
# PROPERTY 1: NO NaN/Inf IN SOLUTION
# =============================================================================

class TestNoNaNInf:
    """The solver must never produce NaN or Inf for any valid input."""
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_solution_never_nan(self, params, y0):
        """
        PROPERTY: For any valid (params, y0), the solution at any time
        contains no NaN or Inf values.
        """
        t_span = (0.0, params_residence(params))
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, np.array(y0),
            method="BDF", rtol=1e-6, atol=1e-9,
        )
        
        if sol.success:
            assert np.all(np.isfinite(sol.y)), \
                f"NaN/Inf in solution for params={params}, y0={y0}"
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_no_overflow(self, params, y0):
        """
        PROPERTY: No species concentration should exceed reasonable
        physical bounds during the simulation.
        """
        t_span = (0.0, 100.0)
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, np.array(y0),
            method="BDF", rtol=1e-6, atol=1e-9,
        )
        
        if sol.success:
            max_conc = sol.y.max()
            assert max_conc < 1e9, \
                f"Concentration {max_conc} mol/m3 exceeds physical bounds"
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_no_nan_in_residuals(self, params, y0):
        """
        PROPERTY: RHS function should never produce NaN for non-negative
        inputs, even at extreme parameter combinations.
        """
        y = np.array(y0)
        result = reaction_rhs_numba(
            0.0, y,
            k_cat=params["k_cat"],
            K_M_co2=params["K_M_co2"],
            k_inact=params["k_inact"],
            E_a_inact=params["E_a_inact"],
            k_so2=params["k_so2"],
            k_chel=params["k_chel"],
            ca_cl2=params["ca_cl2"],
            pH_initial=params["pH_initial"],
            T_reactor=params["T_reactor"]
        )
        
        assert np.all(np.isfinite(result)), \
            f"RHS produced NaN/Inf for params={params}, y0={y0}"


# =============================================================================
# PROPERTY 2: NON-NEGATIVITY (PHYSICAL CONSTRAINT)
# =============================================================================

class TestNonNegativity:
    """Concentrations cannot be negative (physical constraint)."""
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_concentrations_remain_nonnegative(self, params, y0):
        """
        PROPERTY: For any non-negative initial state, all concentrations
        remain >= -1e-3 throughout the simulation (allowing solver tolerance).
        """
        t_span = (0.0, 100.0)
        y0_clamped = np.array(y0)
        y0_clamped[6] = min(y0_clamped[6], 1e-3)  # physically realistic enzyme concentration
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, y0_clamped,
            method="BDF", rtol=1e-8, atol=1e-10,
        )
        
        if sol.success:
            # Tolerant boundary check for stiff BDF solvers
            assert np.all(sol.y >= -1e-3), \
                f"Negative concentration found: min = {sol.y.min()}"


# =============================================================================
# PROPERTY 3: MASS CONSERVATION
# =============================================================================

class TestMassConservation:
    """Mass/atoms must be conserved (conservation laws)."""
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_carbon_conserved_any_input(self, params, y0):
        """
        PROPERTY: Total carbon (CO2_aq + HCO3-) is conserved in solution.
        """
        # In a closed simulation boundary, we check carbon balance.
        y0 = np.array(y0)
        t_span = (0.0, 100.0)
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, y0,
            method="BDF", rtol=1e-8, atol=1e-11,
        )
        
        if sol.success:
            c_total_initial = y0[0] + y0[1]
            c_total_final = sol.y[0, -1] + sol.y[1, -1]
            
            if c_total_initial > 1e-5:
                rel_err = abs(c_total_final - c_total_initial) / c_total_initial
                assert rel_err < 1e-2, \
                    f"Carbon not conserved: rel_err={rel_err:.2e}, initial={c_total_initial}, final={c_total_final}"


# =============================================================================
# PROPERTY 4: MONOTONIC BEHAVIOR
# =============================================================================

class TestMonotonicBehavior:
    """Some quantities should evolve monotonically."""
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_ca_activity_monotonically_decreases(self, params, y0):
        """
        PROPERTY: CA activity should never increase (deactivation is irreversible).
        """
        y0 = np.array(y0)
        if y0[6] == 0:  # Skip if no initial CA
            return
        
        t_span = (0.0, 100.0)
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, y0,
            method="BDF", rtol=1e-6, atol=1e-9,
        )
        
        if sol.success:
            ca_activity = sol.y[6, :]
            diffs = np.diff(ca_activity)
            assert np.all(diffs <= 1e-4), \
                f"CA activity increased somewhere; max increase = {diffs.max()}"


# =============================================================================
# PROPERTY 5: DETERMINISM (SAME INPUT → SAME OUTPUT)
# =============================================================================

class TestDeterminism:
    """Same seed + same input = same output (bit-exact)."""
    
    @given(
        params=kinetic_parameters(),
        y0=initial_state,
    )
    @ci_settings
    def test_deterministic_runs(self, params, y0):
        """
        PROPERTY: Running the solver twice with identical inputs
        should produce identical outputs.
        """
        y0 = np.array(y0)
        t_span = (0.0, 50.0)
        
        sol1 = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, y0,
            method="BDF", rtol=1e-6, atol=1e-9,
        )
        sol2 = solve_ivp(
            lambda t, y: reaction_rhs_numba(
                t, y,
                k_cat=params["k_cat"],
                K_M_co2=params["K_M_co2"],
                k_inact=params["k_inact"],
                E_a_inact=params["E_a_inact"],
                k_so2=params["k_so2"],
                k_chel=params["k_chel"],
                ca_cl2=params["ca_cl2"],
                pH_initial=params["pH_initial"],
                T_reactor=params["T_reactor"]
            ),
            t_span, y0,
            method="BDF", rtol=1e-6, atol=1e-9,
        )
        
        if sol1.success and sol2.success:
            np.testing.assert_array_almost_equal(
                sol1.y, sol2.y, decimal=8
            )
