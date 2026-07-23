"""
Unit tests for Pollutants Database & Assessor.
"""

import pytest
from cbms_sim.domain.pollutants.database import POLLUTANT_DATABASE, PollutantsAssessor


def test_pollutant_database_contains_essential_pollutants():
    assert "CO2" in POLLUTANT_DATABASE
    assert "SO2" in POLLUTANT_DATABASE
    assert "NOx" in POLLUTANT_DATABASE
    assert "PM" in POLLUTANT_DATABASE
    assert "Pb" in POLLUTANT_DATABASE
    assert "Hg" in POLLUTANT_DATABASE

    so2 = POLLUTANT_DATABASE["SO2"]
    assert so2.cpcb_limit_mg_per_nm3 == 200.0
    assert "Gypsum" in so2.primary_system_impact


def test_pollutants_assessor_impact():
    assessor = PollutantsAssessor()
    res = assessor.assess_impact(
        co2_vol_pct=15.0,
        so2_mg_per_nm3=650.0,
        nox_mg_per_nm3=450.0,
        fly_ash_g_per_nm3=30.0,
        exhaust_flow_nm3_hr=10000.0,
    )

    assert res.ph_drop_rate_per_min > 0.0
    assert res.ca_enzyme_inactivation_acceleration_factor > 1.0
    assert res.caso4_scaling_risk_index > 0.5
    assert res.recommended_lime_dosing_kg_per_hr > 0.0
    assert len(res.recommended_control_actions) >= 1
    assert any("SO₂" in action for action in res.recommended_control_actions)
