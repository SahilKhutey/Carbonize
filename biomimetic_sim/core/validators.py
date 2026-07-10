"""
core/validators.py
Pydantic v2 schemas for validating industrial client inputs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum


class IndustryType(str, Enum):
    POWER = "power_generation"
    CEMENT = "cement_manufacturing"
    STEEL = "steel_industry"
    TEXTILE = "textile"
    PETROCHEMICAL = "petrochemical"
    INCINERATOR = "waste_incinerator"


class BoilerType(str, Enum):
    PULVERIZED_COAL = "pulverized_coal"
    CIRCULATING_FLUIDIZED = "cfb"
    STOKER = "stoker_grate"
    DIESEL = "diesel_engine"
    GAS_TURBINE = "gas_turbine"
    KILN = "rotary_kiln"


class CalciumSource(str, Enum):
    LIME = "Ca(OH)2"
    STEEL_SLAG = "steel_slag"
    WASTE_LIME = "waste_lime_mud"
    CEMENT_KILN_DUST = "ckd"


class PlantProfileSchema(BaseModel):
    """Validated input from industrial client."""
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=100)
    industry_type: IndustryType
    boiler_type: BoilerType

    # Flue gas parameters
    exhaust_flow_rate: float = Field(..., gt=100, le=500_000,
                                     description="Nm³/hr")
    baseline_temperature: float = Field(..., ge=80, le=400,
                                       description="°C at stack inlet")
    co2_concentration: float = Field(..., ge=0.1, le=30.0,
                                     description="vol%")
    so2_concentration: float = Field(..., ge=0, le=10_000,
                                     description="mg/Nm³")
    fly_ash_load: float = Field(..., ge=0, le=100,
                                description="g/Nm³")
    nox_concentration: float = Field(default=500.0, ge=0, le=3000,
                                     description="mg/Nm³")

    # Economic inputs
    water_cost_per_kl: float = Field(..., ge=0, le=500, description="INR/kL")
    electricity_cost_per_kwh: float = Field(..., ge=1, le=20, description="INR/kWh")
    chitosan_cost_per_kg: float = Field(default=320.0, ge=100, le=2000)
    calcium_source_type: CalciumSource = CalciumSource.LIME
    calcium_cost_per_ton: float = Field(default=8500.0, ge=0, le=50_000)
    local_brick_market_value: float = Field(default=12.0, ge=5, le=50,
                                           description="INR per block")
    ccts_credit_price: float = Field(default=1850.0, ge=500, le=10_000,
                                     description="INR per tCO2")

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


class SimulationRequestSchema(BaseModel):
    """User-tunable parameters for a simulation run."""
    plant_profile_id: str
    press_force_bar: float = Field(default=200.0, ge=50, le=500)
    enzyme_concentration_mg_l: float = Field(default=12.0, ge=1, le=50)
    chitosan_wt_pct: float = Field(default=3.0, ge=1.0, le=5.0)
    reactor_temperature_c: float = Field(default=40.0, ge=20, le=80)
    override_co2_efficiency: Optional[float] = Field(default=None, ge=0, le=100)
    override_so2_efficiency: Optional[float] = Field(default=None, ge=0, le=100)
