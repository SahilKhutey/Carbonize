"""
tests/test_kinetics.py
Unit tests for the biomineralization ODE kinetics solver.
"""

import pytest
from core.kinetics import solve_reactor_kinetics, BiomineralizationSolver

def test_solver_success_and_bounds():
    """Verify that the BDF kinetics solver converges and output parameters remain bounded."""
    result = solve_reactor_kinetics(
        co2_vol_pct=14.0,
        so2_mg_per_nm3=1200.0,
        flow_nm3_per_hr=10000.0,
        enzyme_mg_per_l=12.0,
        calcium_source_g_per_l=35.0,
        reactor_temp_c=40.0
    )
    
    assert result["solver_success"] is True
    assert 0.0 <= result["co2_capture_efficiency_pct"] <= 100.0
    assert 0.0 <= result["so2_capture_efficiency_pct"] <= 100.0
    assert 0.0 <= result["pm_capture_efficiency_pct"] <= 100.0
    assert 0.0 <= result["metal_chelation_pct"] <= 100.0
    
    # State values must be non-negative
    for state, val in result["final_state"].items():
        assert val >= -1e-5, f"State {state} went negative: {val}"

def test_enzyme_deactivation():
    """Verify high temperatures lead to greater enzyme deactivation."""
    res_cool = solve_reactor_kinetics(reactor_temp_c=25.0)
    res_hot = solve_reactor_kinetics(reactor_temp_c=65.0)
    
    # Deactivation should be higher at 65C than 25C
    assert res_hot["enzyme_deactivation_pct"] > res_cool["enzyme_deactivation_pct"]
