"""Tests for Latin Hypercube Sampling Monte Carlo uncertainty quantification."""

import pytest
import numpy as np

from cbms_sim.domain.uq.monte_carlo import MonteCarloEngine


def test_mc_engine_run(sample_plant, sample_reagent, sample_conditions):
    engine = MonteCarloEngine(n_samples=5, seed=42)
    res = engine.run(sample_plant, sample_reagent, sample_conditions)
    
    assert res.samples.shape == (5, 3)
    assert "co2" in res.statistics
    assert "so2" in res.statistics
    assert res.diagnostics["n_samples"] == 5


def test_mc_seed_reproducibility(sample_plant, sample_reagent, sample_conditions):
    engine1 = MonteCarloEngine(n_samples=5, seed=42)
    engine2 = MonteCarloEngine(n_samples=5, seed=42)
    
    res1 = engine1.run(sample_plant, sample_reagent, sample_conditions)
    res2 = engine2.run(sample_plant, sample_reagent, sample_conditions)
    
    np.testing.assert_array_equal(res1.samples, res2.samples)
