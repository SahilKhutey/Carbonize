"""Direct tests of Numba JIT-compiled kernel functions."""

import numpy as np
import pytest

from cbms_sim.domain.kinetics.kernels import (
    reaction_rhs_numba,
    compute_capture_efficiencies,
)
from cbms_sim.domain.kinetics.extended_engine import extended_rhs_numba


class TestReactionRHS:
    """Test the ODE right-hand side function directly."""
    
    def test_rhs_returns_correct_shape(self, standard_params):
        y = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        result = reaction_rhs_numba(0.0, y, **standard_params)
        assert len(result) == 9
    
    def test_rhs_does_not_modify_input(self, standard_params):
        y = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        y_before = y.copy()
        _ = reaction_rhs_numba(0.0, y, **standard_params)
        np.testing.assert_array_equal(y, y_before)
    
    def test_rhs_handles_negative_inputs(self, standard_params):
        """Negative inputs should be clamped to zero internally."""
        y = np.array([-1.0, 0.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        result = reaction_rhs_numba(0.0, y, **standard_params)
        assert np.all(np.isfinite(result))
    
    def test_rhs_zero_state_returns_zero_or_positive(self, standard_params):
        """At y=0, rates should be zero (no substrate to react)."""
        y = np.zeros(9)
        result = reaction_rhs_numba(0.0, y, **standard_params)
        assert result[0] == 0.0
        assert result[2] == 0.0
    
    def test_rhs_ca_deactivation_is_first_order(self, standard_params):
        """dCA/dt = -k_inact * CA, so doubling CA doubles rate."""
        y1 = np.array([0, 0, 0, 0, 0, 0, 10.0, 0, 0])
        y2 = np.array([0, 0, 0, 0, 0, 0, 20.0, 0, 0])
        
        rate1 = reaction_rhs_numba(0.0, y1, **standard_params)
        rate2 = reaction_rhs_numba(0.0, y2, **standard_params)
        
        np.testing.assert_allclose(rate2[6], 2.0 * rate1[6], rtol=1e-10)
    
    def test_rhs_arrhenius_temperature_scaling(self):
        """k_cat at higher T should be larger (Arrhenius)."""
        y = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        
        params_cold = dict(
            k_cat=1e6, K_M_co2=8.5e-3, k_inact=5e-5, E_a_inact=85e3,
            k_so2=2.5e-2, k_chel=8e-3, ca_cl2=6.75, pH_initial=8.5, T_reactor=293.15,
        )
        params_hot = params_cold.copy()
        params_hot["T_reactor"] = 333.15  # 60°C
        
        rate_cold = reaction_rhs_numba(0.0, y, **params_cold)
        rate_hot = reaction_rhs_numba(0.0, y, **params_hot)
        
        # CA deactivation rate (index 6) should be faster (more negative) at higher T
        assert rate_hot[6] < rate_cold[6]


class TestComputeCaptureEfficiencies:
    """Test the post-processing function."""
    
    def test_zero_capture(self):
        """If final = initial, capture is 0%."""
        initial = np.array([10.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        final = initial.copy()
        eff = compute_capture_efficiencies(initial, final)
        assert eff[0] == 0.0
        assert eff[1] == 0.0
        assert eff[2] == 0.0
        assert eff[3] == 0.0
    
    def test_full_capture(self):
        """If final = 0, capture is 100%."""
        initial = np.array([10.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        final = np.array([0.0, 10.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        eff = compute_capture_efficiencies(initial, final)
        np.testing.assert_allclose(eff[0], 100.0, rtol=1e-6)
        np.testing.assert_allclose(eff[1], 100.0, rtol=1e-6)
    
    def test_clamping(self):
        """Capture should be clamped to [0, 100]."""
        initial = np.array([10.0, 0, 0, 0, 1.0, 0, 0, 0, 0])
        final = np.array([20.0, 0, 0, 0, 2.0, 0, 0, 0, 0])
        eff = compute_capture_efficiencies(initial, final)
        assert np.all(eff >= 0)
        assert np.all(eff <= 100)


class TestExtendedRHS:
    """Test the extended multi-gas Right Hand Side function."""

    def test_extended_rhs_shape(self):
        y = np.zeros(16)
        y[0] = 1.0
        y[1] = 1.0
        y[3] = 100.0
        y[13] = 10**-8.5
        y[14] = 12.0
        
        result = extended_rhs_numba(
            0.0, y,
            k_cat=1.0e6, K_M_co2=8.5, K_i_hco3=26.0,
            k_so2_abs=2.5e-2, K_so2_dissociation=10**-1.85,
            k_no2_abs=1.0e-2, K_no2_dissociation=10**-1.4,
            k_sulfite_oxidation=1.0e-4,
            k_precip_caco3=1.5e-2, k_precip_caso3=1.0e-2, k_precip_caso4=5.0e-3,
            Ksp_caco3=3.3e-9, Ksp_caso4=4.93e-5, Ksp_caso3=6.0e-9,
            k_chel=8.0e-3, free_amine_density=0.05,
            pm_inlet=25.0, k_pm_cap=0.18,
            ca_inactivation=5.0e-5, E_a_inact=85.0e3, T_reactor=313.15
        )
        assert len(result) == 16
