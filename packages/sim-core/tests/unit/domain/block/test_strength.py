"""Tests for composite block strength model."""

import pytest
from decimal import Decimal
from cbms_sim.domain.block.strength import BlockStrengthPredictor
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.models.results import MassBalanceResult


def test_strength_zero_mass():
    predictor = BlockStrengthPredictor()
    # If dry total is zero
    mb = MassBalanceResult(
        input_streams={},
        output_streams={},
        conservation_error_pct=0.0
    )
    # mock output fields
    mb.__dict__["caco3_output_kg_hr"] = 0.0
    mb.__dict__["gypsum_output_kg_hr"] = 0.0
    mb.__dict__["fly_ash_captured_kg_hr"] = 0.0
    mb.__dict__["chitosan_solid_kg_hr"] = 0.0
    
    cond = OperatingConditions()
    res = predictor.predict(mb, cond)
    assert res["compressive_strength_mpa"] == 0.0
    assert res["is_grade"] == "SUBSTANDARD"
    assert res["absorption_pct"] == 100.0
    assert res["leach_risk_class"] == "HIGH"


def test_strength_valid_prediction():
    predictor = BlockStrengthPredictor()
    mb = MassBalanceResult()
    mb.__dict__["caco3_output_kg_hr"] = 50.0
    mb.__dict__["gypsum_output_kg_hr"] = 10.0
    mb.__dict__["fly_ash_captured_kg_hr"] = 40.0
    mb.__dict__["chitosan_solid_kg_hr"] = 3.0
    
    cond = OperatingConditions(
        press_force_bar=Decimal("200.0"),
        curing_time_h=Decimal("48.0")
    )
    res = predictor.predict(mb, cond)
    
    # Check that keys exist
    assert "compressive_strength_mpa" in res
    assert "is_grade" in res
    assert "absorption_pct" in res
    assert "leach_risk_class" in res
    
    # Check boundaries
    assert 1.0 <= res["compressive_strength_mpa"] <= 60.0
    assert res["is_grade"] in ["M25", "M20", "M10", "SUBSTANDARD"]
    assert res["absorption_pct"] > 0
    assert res["leach_risk_class"] in ["LOW", "MEDIUM", "HIGH"]
