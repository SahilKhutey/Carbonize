"""
Verify conservation laws: total mass, total calcium, total sulfur.
"""

from __future__ import annotations

import numpy as np

from tests.numerical.conftest import params_standard, solve_with_method


class TestMassConservation:
    """Total mass in = total mass out."""
    
    def test_calcium_balance(self, standard_initial_state, params_standard):
        y0 = standard_initial_state.copy()
        total_ca_init = y0[2] + y0[3] + y0[5]
        
        t_span = (0.0, 100.0)
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        total_ca_final = y[-1, 2] + y[-1, 3] + y[-1, 5]
        
        rel_err = abs(total_ca_final - total_ca_init) / total_ca_init
        assert rel_err < 1e-4, f"Ca not conserved: rel_err = {rel_err:.2e}"
        
    def test_carbon_balance(self, standard_initial_state, params_standard):
        y0 = standard_initial_state.copy()
        # In this version, CO2_aq + HCO3 is conserved (dCO2_dt + dHCO3_dt = 0)
        total_c_init = y0[0] + y0[1]
        
        t_span = (0.0, 100.0)
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        total_c_final = y[-1, 0] + y[-1, 1]
        
        rel_err = abs(total_c_final - total_c_init) / total_c_init
        assert rel_err < 1e-4, f"C not conserved: rel_err = {rel_err:.2e}"

    def test_sulfur_balance(self, standard_initial_state, params_standard):
        y0 = standard_initial_state.copy()
        params = params_standard.copy()
        params["k_so2"] = 0.0  # Turn off gas absorption to test conservation of initial S
        
        total_s_init = y0[4] + y0[5]
        
        t_span = (0.0, 100.0)
        t, y = solve_with_method(y0, t_span, method="BDF", **params)
        
        total_s_final = y[-1, 4] + y[-1, 5]
        
        rel_err = abs(total_s_final - total_s_init) / max(total_s_init, 1e-15)
        assert rel_err < 1e-4, f"S not conserved: rel_err = {rel_err:.2e}"


class TestMonotonicBehavior:
    """Some quantities must evolve monotonically."""
    
    def test_ca_activity_monotonically_decreasing(
        self, standard_initial_state, params_standard
    ):
        y0 = standard_initial_state.copy()
        t_span = (0.0, 100.0)
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        ca_activity = y[:, 6]
        differences = np.diff(ca_activity)
        assert np.all(differences <= 0.0), f"CA activity increased: {differences[differences > 0]}"
        
    def test_pm_capture_monotonically_increasing(
        self, standard_initial_state, params_standard
    ):
        y0 = standard_initial_state.copy()
        t_span = (0.0, 100.0)
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        pm_trapped = y[:, 8]
        differences = np.diff(pm_trapped)
        assert np.all(differences >= 0.0), f"PM un-trapped: {differences[differences < 0]}"
