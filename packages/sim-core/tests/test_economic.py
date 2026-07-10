"""
tests/test_economic.py
Unit tests for the CAPEX/OPEX economic engine.
"""

import pytest
from core.mass_balance import compute_mass_balance
from core.economic_engine import run_financial_analysis

def test_financial_projections():
    """Verify that economic engine outputs valid capex, opex, and positive return bounds."""
    mass_res = compute_mass_balance(
        flow_nm3_per_hr=10000.0,
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        fly_ash_g_per_nm3=4.5,
        capture_efficiency_overrides={"co2": 90.0, "so2": 98.0}
    )
    
    financial = run_financial_analysis(
        mass_balance=mass_res,
        flow_nm3_per_hr=10000.0
    )
    
    assert financial.capex_total_inr > 0
    assert financial.annual_opex_inr > 0
    assert financial.annual_block_revenue_inr > 0
    assert financial.annual_ccts_revenue_inr > 0
    
    # Payback must be positive or infinity
    assert financial.simple_payback_months > 0
    assert float("-inf") < financial.npv_10yr_inr < float("inf")
