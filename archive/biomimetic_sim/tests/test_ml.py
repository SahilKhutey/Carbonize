"""
tests/test_ml.py
Unit tests for the surrogate modeling and Bayesian optimization scripts.
"""

import pytest
from ml.surrogate_model import KineticsSurrogateModel
from ml.bayesian_optimizer import run_parameter_optimization

def test_surrogate_training_and_inference():
    """Verify that the GP surrogate model trains on sample solver data and yields bounded predictions."""
    model = KineticsSurrogateModel()
    
    # Fit model with a small number of samples to keep tests fast
    model.fit(samples=5)
    
    assert model.fitted is True
    
    # Predict values
    pred = model.predict_capture(enzyme=12.0, temp=40.0, flow=10000.0)
    
    assert 0.0 <= pred["co2_capture_efficiency_pct"] <= 100.0
    assert pred["co2_uncertainty_pct"] >= 0.0
    assert 0.0 <= pred["so2_capture_efficiency_pct"] <= 100.0
    assert pred["so2_uncertainty_pct"] >= 0.0

def test_bayesian_optimization_loop():
    """Verify that the Optuna multi-objective study completes successfully."""
    # Execute a small optimization study of 5 trials
    study = run_parameter_optimization(trials_count=5)
    
    assert len(study.trials) == 5
    assert len(study.best_trials) > 0
    
    # Verify parameter suggestions in best trials
    for trial in study.best_trials:
        params = trial.params
        assert 1.0 <= params["enzyme_concentration_mg_l"] <= 50.0
        assert 1.0 <= params["chitosan_wt_pct"] <= 5.0
        assert 50 <= params["press_force_bar"] <= 500
