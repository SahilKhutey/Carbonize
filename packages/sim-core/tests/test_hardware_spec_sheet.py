"""
Unit tests for HardwareSpecSheetGenerator and Unified Trust Score Gating.
"""

import pytest
from cbms_sim.domain.hardware.spec_sheet import HardwareSpecSheetGenerator


def test_hardware_spec_sheet_validated():
    gen = HardwareSpecSheetGenerator()
    comp_result = {
        "status": "VALIDATED",
        "within_90pct_ci_pct": 95.0,
        "mape_pct": 5.2,
    }
    
    spec = gen.generate(
        exhaust_flow_nm3_hr=10000.0,
        target_co2_capture_pct=85.0,
        comparator_result=comp_result,
        provenance_status="🟢 Bench-validated",
    )
    
    assert spec.target_flue_gas_flow_nm3_hr == 10000.0
    assert spec.applied_safety_margin_pct == 15.0
    assert spec.sized_reactor_volume_m3 > spec.reactor_volume_m3
    assert spec.trust_score.trust_level == "HIGH_CONFIDENCE_VALIDATED"


def test_hardware_spec_sheet_discrepant_gating():
    gen = HardwareSpecSheetGenerator()
    comp_result = {
        "status": "DISCREPANT_MODEL_UNRELIABLE",
        "within_90pct_ci_pct": 10.0,
        "mape_pct": 65.0,
    }
    
    spec = gen.generate(
        exhaust_flow_nm3_hr=10000.0,
        target_co2_capture_pct=85.0,
        comparator_result=comp_result,
        provenance_status="🔴 Estimated/assumed",
    )
    
    assert spec.applied_safety_margin_pct == 50.0  # +50% safety buffer for high-risk model
    assert spec.trust_score.trust_level == "LOW_HIGH_RISK_DISCREPANT"
    assert "HIGH RISK" in spec.trust_score.hardware_guidance_text
