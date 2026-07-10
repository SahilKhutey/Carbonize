"""
tests/test_services.py
Unit tests verifying the Simulation, Reagent, and Plant service layers.
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from cbms_api.services.reagent_service import ReagentService

def test_reagent_service_costing():
    """Verify that ReagentService calculates exact market pricing correctly."""
    service = ReagentService()
    
    cost_data = service.calculate_cost(
        chitosan_wt_pct=3.0,
        ca_wt_pct=3.5,
        enzyme_mg_per_l=12.0
    )
    
    assert cost_data["cost_per_kg_inr"] == (3.0 * 3.20 + 3.5 * 0.085 + 12.0 * 40.0)
    assert cost_data["cost_per_ton_inr"] == cost_data["cost_per_kg_inr"] * 1000.0
    assert "chitosan_inr" in cost_data["breakdown"]
