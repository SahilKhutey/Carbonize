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


def test_mc_engine_correlated_kinetics(sample_plant, sample_reagent, sample_conditions):
    engine = MonteCarloEngine(n_samples=5, seed=42, use_correlated_kinetics=True)
    res = engine.run(sample_plant, sample_reagent, sample_conditions)

    assert res.diagnostics["correlated_kinetics"] is True
    assert "co2" in res.statistics
    assert len(res.statistics["co2"]["samples"]) == 5
    assert "metal" in res.statistics


def test_extended_kinetics_rate_overrides(sample_plant, sample_reagent, sample_conditions):
    from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsEngine, ExtendedKineticsConfig

    # Standard engine
    engine_std = ExtendedKineticsEngine()
    res_std = engine_std.solve(sample_plant, sample_reagent, sample_conditions)

    # Engine with 10x higher k_cat
    config_fast = ExtendedKineticsConfig(rate_overrides={"k_cat": 1.0e7})
    engine_fast = ExtendedKineticsEngine(config=config_fast)
    res_fast = engine_fast.solve(sample_plant, sample_reagent, sample_conditions)

    # Higher k_cat should yield equal or higher CO2 capture efficiency
    assert res_fast.capture_efficiencies["co2_pct"] >= res_std.capture_efficiencies["co2_pct"]

