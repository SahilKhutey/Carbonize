"""Conservation law tests: the ultimate correctness check."""

import pytest
import numpy as np
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba


class TestCarbonConservation:
    """Total carbon (CO2 + HCO3) must be conserved in the 9-species model."""
    
    def test_carbon_conserved_no_reaction(self):
        """If all rates are zero, carbon is trivially conserved."""
        y0 = np.array([10.0, 1.0, 0.0, 0.0, 0.0, 0.0, 12.0, 0.0, 0.0])
        
        params = dict(
            k_cat=0, K_M_co2=0, k_inact=0, E_a_inact=0,
            k_so2=0, k_chel=0, ca_cl2=0, pH_initial=8.5, T_reactor=313.15,
        )
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            (0, 100), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        c_total_initial = y0[0] + y0[1]
        c_total_final = sol.y[0, -1] + sol.y[1, -1]
        
        np.testing.assert_allclose(c_total_final, c_total_initial, rtol=1e-6)
    
    def test_carbon_conserved_with_full_reaction(self, standard_params):
        """Carbon (CO2 + HCO3) is conserved even with full reaction network."""
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 1000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        c_total_initial = y0[0] + y0[1]
        c_total_final = sol.y[0, -1] + sol.y[1, -1]
        
        rel_err = abs(c_total_final - c_total_initial) / c_total_initial
        assert rel_err < 1e-6, f"Carbon not conserved: rel_err={rel_err:.2e}"
    
    def test_carbon_conserved_extreme_pH(self, standard_params):
        """Carbon conservation at pH=5 (CA essentially inactive)."""
        params = standard_params.copy()
        params["pH_initial"] = 5.0
        
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            (0, 500), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        c_initial = y0[0] + y0[1]
        c_final = sol.y[0, -1] + sol.y[1, -1]
        
        rel_err = abs(c_final - c_initial) / c_initial
        assert rel_err < 1e-6


class TestCalciumConservation:
    """Total Ca (Ca2+ + CaCO3_s + CaSO4_s) must be conserved."""
    
    def test_calcium_conserved_full_reaction(self, standard_params):
        y0 = np.array([0.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 1000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        ca_total_initial = y0[2] + y0[3] + y0[5]
        ca_total_final = sol.y[2, -1] + sol.y[3, -1] + sol.y[5, -1]
        
        rel_err = abs(ca_total_final - ca_total_initial) / ca_total_initial
        assert rel_err < 1e-6, f"Calcium not conserved: rel_err={rel_err:.2e}"
    
    def test_calcium_conserved_high_so2(self, standard_params):
        """High SO2 -> all Ca should end up as CaSO4."""
        y0 = np.array([0.0, 0.0, 100.0, 0.0, 50.0, 0.0, 0.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 2000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        ca_total_initial = y0[2] + y0[3] + y0[5]
        ca_total_final = sol.y[2, -1] + sol.y[3, -1] + sol.y[5, -1]
        
        rel_err = abs(ca_total_final - ca_total_initial) / ca_total_initial
        assert rel_err < 1e-6


class TestSulfurConservation:
    """Total S (SO2 + CaSO4) must be conserved when closed to absorption."""
    
    def test_sulfur_conserved(self, standard_params):
        # Disable SO2 gas absorption to close the S balance
        params = standard_params.copy()
        params["k_so2"] = 0.0
        
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 5.0, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **params),
            (0, 1000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        s_total_initial = y0[4] + y0[5]
        s_total_final = sol.y[4, -1] + sol.y[5, -1]
        
        rel_err = abs(s_total_final - s_total_initial) / max(s_total_initial, 1e-15)
        assert rel_err < 1e-6


class TestChargeBalance:
    """Total charge/mass non-negativity check."""
    
    def test_charge_balance_maintained(self, standard_params):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        
        sol = solve_ivp(
            lambda t, y: reaction_rhs_numba(t, y, **standard_params),
            (0, 1000), y0, method="BDF", rtol=1e-9, atol=1e-12
        )
        
        assert np.all(sol.y >= -1e-3), f"Negative concentrations: {sol.y.min()}"
