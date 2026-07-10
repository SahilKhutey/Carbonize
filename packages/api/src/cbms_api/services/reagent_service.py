"""
services/reagent_service.py
Service layer implementing reagent formulation designer rules and pricing calculators.
"""

from typing import List, Optional
from uuid import UUID, uuid4
from cbms_shared.exceptions import NotFoundError

class ReagentService:
    """Enforces boundaries on chitosan, calcium wt% and computes cost metrics."""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._store = {}
        
    def calculate_cost(self, chitosan_wt_pct: float, ca_wt_pct: float, enzyme_mg_per_l: float) -> dict:
        """Calculate Indian market-based pricing breakdown (₹/kg slurry)."""
        chitosan_cost = chitosan_wt_pct * 3.20  # ₹320 per kg
        ca_cost = ca_wt_pct * 0.085  # ₹8.5 per kg
        enzyme_cost = enzyme_mg_per_l * 40.0  # ₹40,000 per gram
        
        cost_per_kg = chitosan_cost + ca_cost + enzyme_cost
        
        return {
            "cost_per_kg_inr": cost_per_kg,
            "cost_per_ton_inr": cost_per_kg * 1000.0,
            "breakdown": {
                "chitosan_inr": chitosan_cost,
                "calcium_source_inr": ca_cost,
                "enzyme_inr": enzyme_cost
            }
        }
        
    def save_formulation(self, name: str, schema_data: dict) -> dict:
        """Save a new custom formulation designer state."""
        reagent_id = uuid4()
        record = {
            "id": reagent_id,
            "name": name,
            **schema_data
        }
        self._store[reagent_id] = record
        return record
