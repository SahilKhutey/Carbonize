"""Tests for kinetics engines (standard and extended)."""

import pytest
from cbms_sim.domain.kinetics import KineticsEngine
from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsEngine
from cbms_shared.exceptions import NumericalDivergenceError


def test_standard_kinetics_engine_solve(sample_plant, sample_reagent, sample_conditions):
    engine = KineticsEngine()
    engine.warmup()
    
    res = engine.solve(sample_plant, sample_reagent, sample_conditions)
    assert res.capture_efficiencies["co2_pct"] > 0.0
    assert res.capture_efficiencies["so2_pct"] >= 0.0
    assert "co2_aq" in res.final_state
    assert res.diagnostics["solver_method"] == "BDF"


def test_extended_kinetics_engine_solve(sample_plant, sample_reagent, sample_conditions):
    engine = ExtendedKineticsEngine()
    engine.warmup()
    
    res = engine.solve(sample_plant, sample_reagent, sample_conditions)
    assert 95.0 < res.capture_efficiencies["co2_pct"] <= 100.0
    assert 10.0 < res.capture_efficiencies["so2_pct"] < 30.0
    assert 95.0 < res.capture_efficiencies["nox_pct"] <= 100.0
    assert 95.0 < res.capture_efficiencies["metal_pct"] <= 100.0
    assert "co2_aq" in res.final_state
    assert res.diagnostics["solver_method"] == "BDF"
