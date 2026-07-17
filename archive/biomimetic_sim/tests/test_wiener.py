"""
tests/test_wiener.py
Unit tests for the Wiener process stochastic saturation model.
"""

import pytest
import numpy as np
from core.wiener_process import simulate_saturation_fpt, predict_saturation_window

def test_wiener_simulation():
    """Verify that Monte Carlo Wiener simulation yields reasonable saturation steps."""
    paths, summary = simulate_saturation_fpt(
        drift_mu_kg_hr=12.0,
        volatility_sigma_kg_hr=3.0,
        capacity_threshold_kg=100.0,
        observation_window_hr=24.0,
        num_paths=100
    )
    
    assert paths.shape == (2400, 100)  # observation_window / time_step
    assert 0.0 <= summary.saturation_within_window_pct <= 100.0
    
    # If it saturates, mean time must be within bounds
    if summary.saturation_within_window_pct > 0:
        assert 0.0 < summary.mean_fpt_hours <= 24.0

def test_analytical_inverse_gaussian():
    """Verify analytical inverse Gaussian calculations match logical conditions."""
    hours = predict_saturation_window(
        drift_mu=12.0,
        volatility_sigma=3.0,
        capacity_kg=100.0,
        confidence=0.95
    )
    
    assert hours > 0
    assert not np.isnan(hours)
