"""
tests/test_uq.py
Unit tests for the Uncertainty Quantification (UQ) and Sensitivity analysis engine.
"""

import pytest
from core.uncertainty_engine import run_uncertainty_analysis

def test_uncertainty_analysis_execution():
    """Verify that LHS sampling propagates uncertainty and computes Spearman sensitivities correctly."""
    uq_res = run_uncertainty_analysis(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        flow_nm3_per_hr=10000.0,
        enzyme_mg_per_l=12.0,
        reactor_temp_c=40.0,
        sample_count=10  # keep sample size small to make test execution fast
    )

    # 1. Assert statistical summary is populated and within bounds
    assert "co2" in uq_res
    assert "so2" in uq_res
    assert "sensitivity" in uq_res

    assert 0.0 <= uq_res["co2"]["mean"] <= 100.0
    assert uq_res["co2"]["std"] >= 0.0
    assert 0.0 <= uq_res["co2"]["p05"] <= 100.0
    assert 0.0 <= uq_res["co2"]["p95"] <= 100.0

    # 2. Assert sensitivity shares sum to approximately 1.0
    sens = uq_res["sensitivity"]
    assert "enzyme_concentration_mg_l" in sens
    assert "reactor_temperature_c" in sens
    assert "flow_rate_nm3_hr" in sens

    total_sens = (
        sens["enzyme_concentration_mg_l"] +
        sens["reactor_temperature_c"] +
        sens["flow_rate_nm3_hr"]
    )
    assert total_sens == pytest.approx(1.0, rel=1e-5)
