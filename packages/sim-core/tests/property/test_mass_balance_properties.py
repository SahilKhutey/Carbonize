"""
Property tests for mass balance engine.
"""

import pytest
from decimal import Decimal
from hypothesis import given
from hypothesis import strategies as st

from cbms_sim.domain.mass_balance.engine import MassBalanceEngine
from .conftest import ci_settings


class TestMassBalanceProperties:
    """Properties that the mass balance engine must satisfy."""
    
    @given(
        flow=st.floats(min_value=100, max_value=500_000, allow_nan=False),
        co2_pct=st.floats(min_value=0.1, max_value=25, allow_nan=False),
        so2_mg=st.floats(min_value=0, max_value=5000, allow_nan=False),
        capture_pct=st.floats(min_value=0, max_value=100, allow_nan=False),
    )
    @ci_settings
    def test_caco3_yield_scales_with_capture(
        self, flow, co2_pct, so2_mg, capture_pct
    ):
        """
        PROPERTY: CaCO3 yield is proportional to CO2 capture
        (stoichiometry 1:1, MW ratio 100.09/44.01).
        """
        # Mock KineticsResult
        class MockKinetics:
            def __init__(self, capture):
                self.capture_efficiencies = {"co2_pct": capture}
        
        # Mock Plant
        class MockPlant:
            def __init__(self, flow, co2, so2):
                self.exhaust_flow_nm3_hr = Decimal(str(flow))
                self.co2_vol_pct = Decimal(str(co2_pct))
                self.so2_mg_per_nm3 = Decimal(str(so2_mg))
                self.fly_ash_g_per_nm3 = Decimal("0")
                self.operating_hours_per_year = 8000
        
        # Mock Reagent
        class MockReagent:
            def __init__(self):
                self.chitosan_wt_pct = Decimal("3.0")
        
        engine = MassBalanceEngine()
        result = engine.compute(
            kinetics=MockKinetics(capture_pct),
            plant=MockPlant(flow, co2_pct, so2_mg),
            reagent=MockReagent(),
        )
        
        # Expected CaCO3 from stoichiometry
        co2_input = flow * (co2_pct / 100) * 44.01 / 22.414  # kg/hr
        expected_caco3 = co2_input * (capture_pct / 100) * (100.09 / 44.01)
        
        if expected_caco3 > 0.1:  # Avoid divide-by-zero
            rel_err = abs(result.caco3_output_kg_hr - expected_caco3) / expected_caco3
            assert rel_err < 0.05, \
                f"CaCO3 yield off: got {result.caco3_output_kg_hr}, expected {expected_caco3}"
