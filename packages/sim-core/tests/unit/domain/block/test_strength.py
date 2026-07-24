"""Tests for composite block strength model."""

import sys
from pathlib import Path
import pytest
from decimal import Decimal

scripts_dir = Path(__file__).resolve().parents[6] / "scripts"
sys.path.append(str(scripts_dir))

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


def test_strength_predictor_matches_calibration_model():
    """Verify that BlockStrengthPredictor and calibration's formulation_strength_response share the same formula."""
    from calibration.models import formulation_strength_response
    
    predictor = BlockStrengthPredictor()
    mb = MassBalanceResult()
    mb.__dict__["caco3_output_kg_hr"] = 97.0
    mb.__dict__["gypsum_output_kg_hr"] = 0.0
    mb.__dict__["fly_ash_captured_kg_hr"] = 0.0
    mb.__dict__["chitosan_solid_kg_hr"] = 3.0  # 3.0 wt%
    
    cond = OperatingConditions(
        press_force_bar=Decimal("50.0"),
        curing_time_h=Decimal("24.0")
    )
    res = predictor.predict(mb, cond)
    
    strength_prod = res["compressive_strength_mpa"]
    strength_calib = formulation_strength_response(
        chitosan_pct=3.0,
        pH=7.0,
        strength_coeff_chitosan=2.6782,
        pH_coeff_strength=0.0,
        press_force_bar=50.0,
        curing_time_h=24.0,
        ash_frac=0.0,
    )
    
    assert pytest.approx(strength_prod, rel=1e-2) == strength_calib

    
    # Check boundaries
    assert 1.0 <= res["compressive_strength_mpa"] <= 60.0
    assert res["is_grade"] in ["M25", "M20", "M10", "SUBSTANDARD"]
    assert res["absorption_pct"] > 0
    assert res["leach_risk_class"] in ["LOW", "MEDIUM", "HIGH"]
