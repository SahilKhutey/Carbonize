"""
Simulation run input schemas with strict validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID


class SimulationCreateRequest(BaseModel):
    """Strict input validation for simulation submission."""
    
    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,
        "str_max_length": 1000,
    }
    
    plant_profile_id: str
    press_force_bar: float = Field(default=200.0, ge=50, le=500)
    enzyme_concentration_mg_l: float = Field(default=12.0, ge=1, le=50)
    chitosan_wt_pct: float = Field(default=3.0, ge=1.0, le=5.0)
    reactor_temperature_c: float = Field(default=40.0, ge=20, le=80)
    override_co2_efficiency: Optional[float] = Field(default=None, ge=0, le=100)
    override_so2_efficiency: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator("plant_profile_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError("plant_profile_id must be a valid UUID")
