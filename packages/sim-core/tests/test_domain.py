"""
tests/test_domain.py
Unit tests verifying the cbms_sim domain module integrations.
"""

from decimal import Decimal
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.kinetics.engine import solve_kinetics
from cbms_sim.domain.mass_balance.engine import MassBalanceEngine

def test_restructured_domain_solve():
    """Verify that kinetics and mass balance engines compile and execute correctly."""
    plant = PlantProfile(
        name="Test Power Station",
        co2_vol_pct=Decimal("14.0"),
        so2_mg_per_nm3=Decimal("1200.0")
    )
    
    reagent = ReagentFormulation(
        chitosan_wt_pct=Decimal("3.0"),
        enzyme_mg_per_l=Decimal("12.0")
    )
    
    conditions = OperatingConditions(
        reactor_temp_c=Decimal("40.0")
    )
    
    # 1. Kinetics
    kin_res = solve_kinetics(plant, reagent, conditions)
    assert kin_res.capture_efficiencies["co2_pct"] > 0.0
    assert kin_res.capture_efficiencies["so2_pct"] >= 0.0
    
    # 2. Mass Balance
    mb_engine = MassBalanceEngine()
    mb_res = mb_engine.compute(kin_res, plant, reagent)
    assert mb_res.conservation_error_pct < 0.5
    assert mb_res.co2_capture_pct >= 0.0
