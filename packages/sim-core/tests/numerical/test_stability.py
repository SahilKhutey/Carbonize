"""
Edge case stability tests: solver should not crash or give garbage
output for extreme input values.
"""

from __future__ import annotations

import numpy as np

from tests.numerical.conftest import solve_with_method


class TestNearZeroConcentrations:
    """System at very low (near-zero) concentrations."""
    
    def test_zero_initial_state_doesnt_crash(self, params_standard):
        y0 = np.zeros(9)
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        assert np.all(y >= -1e-4), f"Negative concentrations appeared: min={y.min()}"
    
    def test_very_small_concentrations(self, params_standard):
        y0 = np.array([1e-12, 1e-12, 1e-12, 0.0, 1e-12, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        assert np.all(np.isfinite(y)), f"NaN/Inf appeared: {y[~np.isfinite(y)]}"
        assert np.all(y >= -1e-4)
    
    def test_mixed_zero_nonzero(self, params_standard):
        y0 = np.array([0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        assert np.all(np.isfinite(y))
        assert y[-1, 6] < 12.0
        assert y[-1, 6] > 0.0


class TestExtremeTemperature:
    """Extreme temperatures stress both kinetics and stiffness."""
    
    def test_extreme_hot_70c(self, params_extreme_hot):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_extreme_hot)
        
        assert np.all(np.isfinite(y))
        ca_deactivation_pct = (1.0 - y[-1, 6] / 12.0) * 100.0
        assert ca_deactivation_pct > 1.0
    
    def test_extreme_cold_10c(self, params_extreme_cold):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_extreme_cold)
        
        assert np.all(np.isfinite(y))
        ca_deactivation_pct = (1.0 - y[-1, 6] / 12.0) * 100.0
        assert ca_deactivation_pct < 10.0


class TestExtremePH:
    """Extreme pH values — CA activity is pH-dependent."""
    
    def test_extreme_acidic_pH5(self, params_extreme_ph_acidic):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_extreme_ph_acidic)
        
        # Verify it runs successfully without crash/nans
        assert np.all(np.isfinite(y))
    
    def test_extreme_basic_pH11(self, params_extreme_ph_basic):
        y0 = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        t_span = (0.0, 27.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_extreme_ph_basic)
        
        assert np.all(np.isfinite(y))
        assert y[-1, 6] >= -1e-4


class TestLongHorizon:
    """Stability over long simulation times."""
    
    def test_long_horizon_1_hour(self, standard_initial_state, params_standard):
        y0 = standard_initial_state
        t_span = (0.0, 3600.0)
        
        t, y = solve_with_method(y0, t_span, method="BDF", **params_standard)
        
        assert np.all(np.isfinite(y))
        assert np.all(y >= -1e-4)
        ca_remaining_pct = y[-1, 6] / 12.0 * 100.0
        assert ca_remaining_pct < 85.0
