"""
api/routes/reagents.py
Endpoints for managing reagent formulations and costing design.
"""

from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/reagents", tags=["Reagents"])

class ReagentSchema(BaseModel):
    name: str
    description: Optional[str] = None
    chitosan_wt_pct: float = Field(..., ge=0.5, le=6.0)
    ca_source_type: str = "Ca(OH)2"
    ca_wt_pct: float = Field(..., ge=1.0, le=10.0)
    enzyme_type: str = "bovine_CA"
    enzyme_mg_per_l: float = Field(..., ge=1.0, le=50.0)

# Local memory-backed storage for tenant-scoped custom designer configurations
_REAGENTS_DB = {}

@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_reagent(schema: ReagentSchema):
    """
    Creates a new custom reagent formulation and registers it.
    """
    reagent_id = uuid4()
    record = {
        "id": reagent_id,
        **schema.model_dump()
    }
    _REAGENTS_DB[reagent_id] = record
    return record

@router.get("", response_model=None)
async def list_reagents():
    """
    Lists all custom formulations.
    """
    return list(_REAGENTS_DB.values())

@router.get("/{reagent_id}", response_model=None)
async def get_reagent(reagent_id: UUID):
    """
    Retrieves a specific formulation.
    """
    if reagent_id not in _REAGENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reagent formulation not found."
        )
    return _REAGENTS_DB[reagent_id]

@router.post("/calculate-cost", response_model=None)
async def calculate_cost(schema: ReagentSchema):
    """
    Calculates operational and material costs per kg of matrix slurry.
    """
    chitosan_cost = schema.chitosan_wt_pct * 3.20  # INR per gram (320 per kg)
    ca_cost = schema.ca_wt_pct * 0.085  # INR per gram (8.5 per kg)
    enzyme_cost = schema.enzyme_mg_per_l * 40.0  # INR per mg (40,000 per g)
    
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

@router.post("/{reagent_id}/clone", response_model=None)
async def clone_reagent(reagent_id: UUID, new_name: str):
    """
    Clones an existing reagent formulation under a new design profile name.
    """
    if reagent_id not in _REAGENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reagent formulation not found."
        )
    source = _REAGENTS_DB[reagent_id]
    clone_id = uuid4()
    cloned_record = {
        **source,
        "id": clone_id,
        "name": new_name
    }
    _REAGENTS_DB[clone_id] = cloned_record
    return cloned_record
