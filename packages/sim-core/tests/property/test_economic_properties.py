"""
Property tests for economic model.
"""

import pytest
import numpy as np
from decimal import Decimal

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from cbms_sim.domain.economic.engine import EconomicEngine


class TestEconomicProperties:
    """Properties of the economic model."""
    
    @given(
        capex=st.floats(min_value=1e6, max_value=1e9, allow_nan=False),
        annual_opex=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
        annual_revenue=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
        lifetime_years=st.integers(min_value=1, max_value=20),
        discount_rate=st.floats(min_value=0.0, max_value=0.30, allow_nan=False),
    )
    @settings(max_examples=1000)
    def test_npv_increases_with_revenue(self, capex, annual_opex, annual_revenue, lifetime_years, discount_rate):
        """
        PROPERTY: NPV is monotonically increasing in annual_revenue
        (when other parameters fixed).
        """
        engine = EconomicEngine()
        
        result1 = engine.compute_npv(
            capex=capex, annual_opex=annual_opex, annual_revenue=annual_revenue,
            lifetime_years=lifetime_years, discount_rate=discount_rate,
        )
        result2 = engine.compute_npv(
            capex=capex, annual_opex=annual_opex, annual_revenue=annual_revenue * 1.1,
            lifetime_years=lifetime_years, discount_rate=discount_rate,
        )
        
        # Higher revenue → higher NPV
        assert result2.npv > result1.npv
    
    @given(
        capex=st.floats(min_value=1e6, max_value=1e9, allow_nan=False),
        annual_opex=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
        annual_revenue=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
        lifetime_years=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=500)
    def test_npv_zero_discount_equals_sum(self, capex, annual_opex, annual_revenue, lifetime_years):
        """
        PROPERTY: With zero discount rate, NPV = -CAPEX + lifetime × net_annual.
        """
        engine = EconomicEngine()
        
        result = engine.compute_npv(
            capex=capex, annual_opex=annual_opex, annual_revenue=annual_revenue,
            lifetime_years=lifetime_years, discount_rate=0.0,
        )
        
        expected = -capex + lifetime_years * (annual_revenue - annual_opex)
        np.testing.assert_allclose(result.npv, expected, rtol=1e-6)
    
    @given(
        capex=st.floats(min_value=1e6, max_value=1e9, allow_nan=False),
        annual_opex=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
        annual_revenue=st.floats(min_value=1e5, max_value=1e8, allow_nan=False),
    )
    @settings(max_examples=1000)
    def test_payback_defined_only_if_profitable(
        self, capex, annual_opex, annual_revenue
    ):
        """
        PROPERTY: If annual_revenue <= annual_opex, project never
        pays back (payback should be infinity).
        """
        assume(annual_revenue <= annual_opex)
        
        engine = EconomicEngine()
        result = engine.compute_payback(
            capex=capex, annual_opex=annual_opex, annual_revenue=annual_revenue,
        )
        
        assert result.payback_months > 1000 or result.payback_months == float('inf')
