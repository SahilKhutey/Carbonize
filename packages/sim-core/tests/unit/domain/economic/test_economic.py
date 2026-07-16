"""Tests for the EconomicEngine module."""

import pytest
from cbms_sim.domain.economic.engine import EconomicEngine
from cbms_sim.domain.models.results import MassBalanceResult


def test_economic_engine_calculations():
    engine = EconomicEngine()
    mb = MassBalanceResult(
        conservation_error_pct=0.0
    )
    # mock required mass balance inputs
    mb.__dict__["co2_input_kg_hr"] = 1000.0
    mb.__dict__["co2_capture_pct"] = 90.0
    mb.__dict__["ca_reagent_input_kg_hr"] = 500.0
    mb.__dict__["chitosan_input_kg_hr"] = 15.0
    
    res = engine.compute(mb, strength_mpa=25.0, operating_hours_per_year=8000)
    
    assert res["capex_inr"] == 1.2e8
    assert res["annual_opex_inr"] > 0.0
    assert res["annual_revenue_inr"] > 0.0
    assert "npv_10yr_inr" in res
    assert "payback_months" in res
    
    # NPV discount cashflow correctness checks
    assert res["payback_months"] > 0.0


def test_economic_engine_negative_cashflow():
    engine = EconomicEngine()
    mb = MassBalanceResult()
    # extremely high reagent consumption with low capture to force negative cashflow
    mb.__dict__["co2_input_kg_hr"] = 10.0
    mb.__dict__["co2_capture_pct"] = 1.0
    mb.__dict__["ca_reagent_input_kg_hr"] = 100000.0
    mb.__dict__["chitosan_input_kg_hr"] = 50000.0
    
    res = engine.compute(mb, strength_mpa=5.0, operating_hours_per_year=8000)
    assert res["payback_months"] == 999.0
