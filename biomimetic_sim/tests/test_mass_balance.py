"""
tests/test_mass_balance.py
Unit tests for the multi-pollutant mass balance solver.
"""

import pytest
from core.mass_balance import compute_mass_balance

def test_mass_conservation():
    """Verify that total mass inputs match total mass outputs within 1% tolerance."""
    res = compute_mass_balance(
        flow_nm3_per_hr=10000.0,
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        fly_ash_g_per_nm3=4.5,
        chitosan_wt_pct=3.0,
        capture_efficiency_overrides={"co2": 90.0, "so2": 98.0}
    )
    
    assert res.mass_balance_error_pct < 1.0
    assert res.co2_input > 0
    assert res.caco3_output > 0
    assert res.cpcb_compliant is True

def test_compliance_limits():
    """Verify high SO2 concentrations breach CPCB compliance limits."""
    # Extremely high SO2 input (10,000 mg/Nm³) with a low capture efficiency
    res = compute_mass_balance(
        flow_nm3_per_hr=10000.0,
        co2_vol_pct=14.0,
        so2_mg_per_nm3=10000.0,
        fly_ash_g_per_nm3=4.5,
        capture_efficiency_overrides={"co2": 50.0, "so2": 10.0}
    )
    
    assert res.cpcb_compliant is False
