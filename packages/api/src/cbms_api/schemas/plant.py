"""
Plant profile input schemas with strict validation.
"""

from pydantic import BaseModel, Field, field_validator
from core.validators import BoilerType, IndustryType, CalciumSource


class PlantProfileCreateRequest(BaseModel):
    """Strict input validation for plant profile creation."""
    
    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,
        "str_max_length": 1000,
    }
    
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=100)
    industry_type: IndustryType
    boiler_type: BoilerType

    # Flue gas parameters
    exhaust_flow_rate: float = Field(..., gt=100, le=500_000)
    baseline_temperature: float = Field(..., ge=80, le=400)
    co2_concentration: float = Field(..., ge=0.1, le=30.0)
    so2_concentration: float = Field(..., ge=0, le=10_000)
    fly_ash_load: float = Field(..., ge=0, le=100)
    nox_concentration: float = Field(default=500.0, ge=0, le=3000)

    # Economic inputs
    water_cost_per_kl: float = Field(..., ge=0, le=500)
    electricity_cost_per_kwh: float = Field(..., ge=1, le=20)
    chitosan_cost_per_kg: float = Field(default=320.0, ge=100, le=2000)
    calcium_source_type: CalciumSource = CalciumSource.LIME
    calcium_cost_per_ton: float = Field(default=8500.0, ge=0, le=50_000)
    local_brick_market_value: float = Field(default=12.0, ge=5, le=50)
    ccts_credit_price: float = Field(default=1850.0, ge=500, le=10_000)

    @field_validator("co2_concentration")
    @classmethod
    def validate_co2_range(cls, v):
        if v > 25.0:
            raise ValueError("CO2 concentration > 25% — verify flue gas source.")
        return v

    @field_validator("exhaust_flow_rate")
    @classmethod
    def validate_flow_range(cls, v):
        if v > 200_000:
            raise ValueError(
                "Flow > 200,000 Nm³/hr requires multi-train configuration. "
                "Contact engineering for parallel unit design."
            )
        return v
