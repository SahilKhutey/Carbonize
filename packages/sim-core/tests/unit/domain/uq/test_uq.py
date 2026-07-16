"""Tests for SobolAnalyzer and FirstPassageTime modules."""

import pytest
import numpy as np
from cbms_sim.domain.uq.fpt import FirstPassageTime
from cbms_sim.domain.uq.sobol import SobolAnalyzer
from cbms_sim.domain.models.results import UQResult


def test_fpt_drift_positive():
    fpt = FirstPassageTime()
    res = fpt.analytical_fpt(threshold=10.0, drift=2.0, diffusion=0.5)
    
    assert res["mean_fpt_hours"] == 5.0
    assert res["mode_fpt_hours"] > 0.0
    assert res["variance_fpt_hours"] > 0.0


def test_fpt_drift_zero_or_negative():
    fpt = FirstPassageTime()
    res = fpt.analytical_fpt(threshold=10.0, drift=0.0, diffusion=0.5)
    
    assert res["mean_fpt_hours"] == float("inf")
    assert res["mode_fpt_hours"] == 0.0
    assert res["variance_fpt_hours"] == float("inf")


def test_sobol_empty_samples():
    analyzer = SobolAnalyzer()
    uq_res = UQResult(
        samples=np.array([]),
        statistics={},
        diagnostics={}
    )
    res = analyzer.analyze(uq_res)
    assert res["enzyme_concentration_mg_l"] == pytest.approx(0.333, abs=1e-3)
    assert res["reactor_temperature_c"] == pytest.approx(0.333, abs=1e-3)
    assert res["flow_rate_nm3_hr"] == pytest.approx(0.333, abs=1e-3)


def test_sobol_valid_samples():
    analyzer = SobolAnalyzer()
    # 10 samples of 3 variables
    samples = np.random.default_rng(42).uniform(0, 10, (10, 3))
    uq_res = UQResult(
        samples=samples,
        statistics={},
        diagnostics={}
    )
    res = analyzer.analyze(uq_res)
    
    assert 0.0 <= res["enzyme_concentration_mg_l"] <= 1.0
    assert 0.0 <= res["reactor_temperature_c"] <= 1.0
    assert 0.0 <= res["flow_rate_nm3_hr"] <= 1.0
    assert pytest.approx(res["enzyme_concentration_mg_l"] + res["reactor_temperature_c"] + res["flow_rate_nm3_hr"]) == 1.0
