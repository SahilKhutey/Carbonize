"""
Public type definitions for sim-core v1 API.

All types use Pydantic v2 for:
- Automatic validation
- JSON serialization
- OpenAPI schema generation
- IDE autocomplete

All units are SI by default. Convert at API boundaries.
"""

from pydantic import BaseModel, Field, field_validator
from pydantic_core import core_schema
from typing import Literal, Optional, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


# =============================================================================
# ENUMS
# =============================================================================

class SimulationType(str, Enum):
    """Simulation execution mode."""
    BASELINE = "baseline"              # Single deterministic solve, no UQ
    MONTE_CARLO = "monte_carlo"        # MC UQ only
    SOBOL = "sobol"                    # MC + Sobol sensitivity
    FULL = "full"                      # MC + Sobol + critical experiments


class CalciumSourceType(str, Enum):
    """Type of calcium source for the matrix."""
    LIME = "Ca(OH)2"
    STEEL_SLAG = "steel_slag"
    WASTE_LIME = "waste_lime"
    CEMENT_KILN_DUST = "ckd"


class BoilerType(str, Enum):
    """Type of boiler / industrial process."""
    PULVERIZED_COAL = "pulverized_coal"
    CIRCULATING_FLUIDIZED = "cfb"
    STOKER_GRATE = "stoker_grate"
    DIESEL_ENGINE = "diesel"
    GAS_TURBINE = "gas_turbine"
    ROTARY_KILN = "rotary_kiln"


class SimulationStatus(str, Enum):
    """Simulation execution status."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class HeavyMetal(str, Enum):
    """Supported heavy metals."""
    HG = "Hg"
    PB = "Pb"
    CD = "Cd"
    AS = "As"
    CR = "Cr"
    NI = "Ni"
    ZN = "Zn"


# =============================================================================
# INPUT TYPES
# =============================================================================

class PlantProfile(BaseModel):
    """
    Industrial plant emission profile.
    
    SI units throughout. Convert from operational units at API boundary.
    
    All values must be non-negative. Concentration ranges validated
    against physical limits (0-100% for vol%, etc.).
    """
    model_config = {"frozen": True, "extra": "forbid"}
    
    # Identity
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., max_length=255)
    boiler_type: BoilerType
    
    # Flow and temperature
    exhaust_flow_nm3_hr: Decimal = Field(
        ..., gt=0, le=1_000_000,
        description="Exhaust gas volumetric flow at STP (Nm³/hr)"
    )
    baseline_temperature_c: Decimal = Field(
        ..., ge=0, le=500,
        description="Flue gas temperature at stack inlet (°C)"
    )
    
    # Pollutant concentrations
    co2_vol_pct: Decimal = Field(
        ..., ge=0, le=100,
        description="CO₂ concentration in dry flue gas (vol%)"
    )
    so2_mg_per_nm3: Decimal = Field(
        ..., ge=0, le=100_000,
        description="SO₂ concentration (mg/Nm³)"
    )
    nox_mg_per_nm3: Decimal = Field(
        ..., ge=0, le=10_000,
        description="NOₓ concentration as NO₂ (mg/Nm³)"
    )
    fly_ash_g_per_nm3: Decimal = Field(
        ..., ge=0, le=1000,
        description="Particulate matter concentration (g/Nm³)"
    )
    heavy_metal_profile: list[dict] = Field(
        default_factory=list,
        description="[{\"element\": \"Hg\", \"conc_ug_per_nm3\": 5.0}, ...]"
    )
    
    # Operating schedule
    operating_hours_per_year: int = Field(
        default=8000, ge=0, le=8760,
        description="Annual operating hours"
    )
    
    @field_validator("heavy_metal_profile")
    @classmethod
    def validate_heavy_metals(cls, v: list[dict]) -> list[dict]:
        for entry in v:
            if "element" not in entry or "conc_ug_per_nm3" not in entry:
                raise ValueError(
                    "Each heavy metal entry must have 'element' and 'conc_ug_per_nm3'"
                )
            element = entry["element"]
            if element not in [m.value for m in HeavyMetal]:
                raise ValueError(f"Unsupported heavy metal: {element}")
            conc = entry["conc_ug_per_nm3"]
            if not (0 <= conc <= 1_000_000):
                raise ValueError(f"Concentration {conc} out of range [0, 1e6] µg/Nm³")
        return v


class ReagentFormulation(BaseModel):
    """
    Biomimetic matrix formulation.
    
    All percentages are weight percent (wt%) in the liquid matrix.
    """
    model_config = {"frozen": True, "extra": "forbid"}
    
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    
    # Matrix composition
    chitosan_wt_pct: Decimal = Field(
        ..., ge=Decimal("0.1"), le=Decimal("10.0"),
        description="Chitosan concentration (wt% of liquid matrix)"
    )
    ca_source_type: CalciumSourceType
    ca_wt_pct: Decimal = Field(
        ..., ge=Decimal("0.1"), le=Decimal("20.0"),
        description="Calcium source concentration (wt%)"
    )
    
    # Enzyme
    enzyme_type: str = Field(default="bovine_CA", max_length=100)
    enzyme_mg_per_l: Decimal = Field(
        ..., gt=0, le=100,
        description="Enzyme concentration in matrix (mg/L)"
    )
    
    # Additives (optional)
    additives: list[dict] = Field(
        default_factory=list,
        description="Optional buffer additives"
    )


class OperatingConditions(BaseModel):
    """
    Reactor operating conditions.
    
    All values must be within physically reasonable ranges.
    """
    model_config = {"frozen": True, "extra": "forbid"}
    
    reactor_temp_c: Decimal = Field(
        ..., ge=0, le=100,
        description="Reactor temperature (°C)"
    )
    pH_initial: Decimal = Field(
        ..., ge=0, le=14,
        description="Initial slurry pH"
    )
    liquid_to_gas_ratio: Decimal = Field(
        ..., ge=Decimal("0.1"), le=Decimal("100"),
        description="L/G ratio (L liquid per m³ gas)"
    )
    residence_time_s: Decimal = Field(
        ..., gt=0, le=3600,
        description="Gas residence time in reactor (seconds)"
    )
    mesh_count: int = Field(default=6, ge=1, le=50)
    press_force_bar: Decimal = Field(
        default=Decimal("200"), ge=10, le=1000,
        description="Hydraulic press force for block formation (bar)"
    )
    curing_temperature_c: Decimal = Field(
        default=Decimal("25"), ge=0, le=80
    )
    curing_time_h: Decimal = Field(
        default=Decimal("48"), ge=1, le=720
    )


class SimulationOptions(BaseModel):
    """Optional simulation configuration."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    simulation_type: SimulationType = SimulationType.MONTE_CARLO
    n_mc_samples: int = Field(default=500, ge=100, le=100000)
    include_sensitivity: bool = Field(default=False)
    random_seed: Optional[int] = Field(default=42, description="None for non-deterministic")
    timeout_seconds: int = Field(default=1800, ge=10, le=7200)


class SimulationRequest(BaseModel):
    """
    Complete input to a simulation run.
    
    This is the v1 API's primary input type. All downstream code
    (API, workers) should accept this and pass it to the engine.
    """
    model_config = {"frozen": True, "extra": "forbid"}
    
    # Identifiers (for tracking)
    request_id: UUID
    org_id: UUID
    user_id: UUID
    
    # Inputs
    plant: PlantProfile
    reagent: ReagentFormulation
    conditions: OperatingConditions
    options: SimulationOptions = Field(default_factory=SimulationOptions)
    
    # Metadata
    submitted_at: datetime
    parameter_set_version: str = Field(default="v2026.1")
    code_version: str = Field(default="0.1.0")
    
    @field_validator("plant")
    @classmethod
    def validate_plant_compatibility(cls, v: PlantProfile) -> PlantProfile:
        # Add cross-field validations here
        return v


# =============================================================================
# OUTPUT TYPES
# =============================================================================

class CaptureEfficiency(BaseModel):
    """Pollutant capture efficiency with uncertainty."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    co2_pct: float = Field(..., ge=0, le=100, description="CO₂ capture (%)")
    so2_pct: float = Field(..., ge=0, le=100, description="SO₂ capture (%)")
    pm_pct: float = Field(..., ge=0, le=100, description="PM capture (%)")
    metal_pct: float = Field(..., ge=0, le=100, description="Heavy metal capture (%)")
    
    # Units
    units: str = Field(default="percent", frozen=True)
    
    # Quality indicator
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM",
        description="Based on input data quality and parameter certainty"
    )


class DistributionStats(BaseModel):
    """Statistical summary of a Monte Carlo output distribution."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    mean: float
    std: float = Field(..., ge=0)
    min: float
    max: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    cv: float = Field(..., ge=0, description="Coefficient of variation (std/mean)")
    n_samples: int = Field(..., gt=0)
    samples: Optional[list[float]] = None


class KineticsResult(BaseModel):
    """Output of reaction kinetics simulation."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    capture: CaptureEfficiency
    
    # Time series (optional, for plots)
    time_s: Optional[list[float]] = Field(
        default=None, description="Time points (s) — null for baseline"
    )
    co2_aq_mol_per_m3: Optional[list[float]] = None
    hco3_mol_per_m3: Optional[list[float]] = None
    ca_free_mol_per_m3: Optional[list[float]] = None
    caco3_solid_mol_per_m3: Optional[list[float]] = None
    ca_active_mg_per_l: Optional[list[float]] = None
    
    # Diagnostics
    nfev: int = Field(..., ge=0, description="ODE function evaluations")
    njev: int = Field(..., ge=0, description="ODE Jacobian evaluations")
    nlu: int = Field(..., ge=0, description="LU decompositions")
    solver_message: str = ""
    computation_time_s: float = Field(..., ge=0)
    converged: bool
    
    # Provenance
    input_hash: str = Field(..., description="SHA-256 of input parameters")
    parameter_set_version: str
    code_version: str


class MassBalanceResult(BaseModel):
    """Output of mass balance calculation."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    # Input streams (kg/hr)
    co2_input_kg_hr: float = Field(..., ge=0)
    so2_input_kg_hr: float = Field(..., ge=0)
    fly_ash_input_kg_hr: float = Field(..., ge=0)
    ca_reagent_input_kg_hr: float = Field(..., ge=0)
    chitosan_input_kg_hr: float = Field(..., ge=0)
    
    # Output streams (kg/hr)
    caco3_output_kg_hr: float = Field(..., ge=0)
    gypsum_output_kg_hr: float = Field(..., ge=0)
    fly_ash_captured_kg_hr: float = Field(..., ge=0)
    bound_water_kg_hr: float = Field(..., ge=0)
    
    # Conservation check
    conservation_error_pct: float = Field(..., description="|in - out| / in × 100")
    cpcb_so2_compliant: bool
    so2_outlet_mg_per_nm3: float = Field(..., ge=0)
    
    units: str = Field(default="kg_per_hour", frozen=True)


class BlockProperties(BaseModel):
    """Properties of the cured solid block product."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    strength_mpa: float = Field(..., ge=0, le=200, description="Compressive strength (MPa)")
    density_kg_per_m3: float = Field(..., ge=0, le=5000)
    water_absorption_pct: float = Field(..., ge=0, le=100)
    
    # IS grade classification
    is_grade: Literal["M25", "M20", "M10", "IS_1077_A", "IS_2185_A", "SUBSTANDARD"]
    
    # Composition (wt%)
    caco3_fraction: float = Field(..., ge=0, le=1)
    gypsum_fraction: float = Field(..., ge=0, le=1)
    ash_fraction: float = Field(..., ge=0, le=1)
    chitosan_fraction: float = Field(..., ge=0, le=1)
    
    # Leach risk (qualitative)
    leach_risk: Literal["LOW", "MEDIUM", "HIGH"]


class EconomicResult(BaseModel):
    """Output of economic analysis."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    # Costs
    capex_inr: float = Field(..., ge=0, description="Capital expenditure (INR)")
    annual_opex_inr: float = Field(..., ge=0)
    annual_revenue_inr: float = Field(..., ge=0)
    
    # Revenues
    ccts_revenue_inr: float = Field(..., ge=0)
    block_revenue_inr: float = Field(..., ge=0)
    
    # Metrics
    npv_10yr_inr: float
    irr_pct: float
    payback_months: float = Field(..., gt=0)
    
    currency: str = Field(default="INR", frozen=True)
    base_year: int = Field(default=2026, frozen=True)


class Sensitivities(BaseModel):
    """Sobol sensitivity analysis results."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    first_order: dict[str, float] = Field(
        default_factory=dict,
        description="First-order Sobol indices {param_name: S_1}"
    )
    total_order: dict[str, float] = Field(
        default_factory=dict,
        description="Total-order Sobol indices {param_name: S_T}"
    )
    npv_first_order: Optional[dict[str, float]] = None
    block_strength_first_order: Optional[dict[str, float]] = None
    critical_experiments: list[dict] = Field(
        default_factory=list,
        description="Top experiments ranked by impact"
    )
    
    n_base_samples: int = Field(..., ge=0)
    method: str = Field(default="Saltelli")


class ComplianceFlags(BaseModel):
    """Regulatory compliance status."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    cpcb_so2_compliant: bool
    cpcb_pm_compliant: bool
    ccts_eligible: bool
    is_grade_acceptable: bool
    
    so2_outlet_mg_per_nm3: float = Field(..., ge=0)
    pm_outlet_mg_per_nm3: float = Field(..., ge=0)
    so2_outlet_limit_mg_per_nm3: float = Field(default=200.0)
    pm_outlet_limit_mg_per_nm3: float = Field(default=30.0)
    
    notes: list[str] = Field(default_factory=list)


class SimulationResult(BaseModel):
    """
    Complete output of a simulation run.
    
    This is the v1 API's primary output type. All downstream code
    (API, workers, UI) should consume this.
    """
    model_config = {"frozen": True, "extra": "forbid"}
    
    # Identity
    request_id: UUID
    run_id: UUID
    org_id: UUID
    
    # Status
    status: SimulationStatus
    status_message: str = ""
    error_code: Optional[str] = None
    
    # Component results (all optional because baseline returns only kinetics)
    kinetics: Optional[KineticsResult] = None
    mass_balance: Optional[MassBalanceResult] = None
    block: Optional[BlockProperties] = None
    economic: Optional[EconomicResult] = None
    sensitivity: Optional[Sensitivities] = None
    compliance: Optional[ComplianceFlags] = None
    
    # Uncertainty (only populated for MC / SOBOL simulations)
    capture_distribution: Optional[DistributionStats] = None
    npv_distribution: Optional[DistributionStats] = None
    payback_distribution: Optional[DistributionStats] = None
    so2_distribution: Optional[DistributionStats] = None
    strength_distribution: Optional[DistributionStats] = None
    
    # Metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_wall_clock_s: Optional[float] = Field(default=None, ge=0)
    output_hash: str = Field(..., description="SHA-256 of full result")
    
    # Provenance
    parameter_set_version: str
    code_version: str
    
    @property
    def is_complete(self) -> bool:
        return self.status == SimulationStatus.COMPLETED
    
    @property
    def is_successful(self) -> bool:
        return self.status == SimulationStatus.COMPLETED and self.error_code is None


# =============================================================================
# PARAMETER SET TYPES
# =============================================================================

class ParameterSetVersion(str):
    """Semantic version string (MAJOR.MINOR.PATCH)."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )
        
    @classmethod
    def validate(cls, v: Any) -> "ParameterSetVersion":
        if not isinstance(v, str):
            raise TypeError("Version must be a string")
        parts = v.lstrip('v').split('.')
        if len(parts) < 2 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Invalid version format: {v}. Expected e.g. 'v2026.1' or '1.0.0'")
        return cls(v)


class ParameterSet(BaseModel):
    """Versioned parameter set with provenance."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    version: ParameterSetVersion
    description: str = ""
    created_at: datetime
    parameters: dict[str, dict]  # Nested: {category: {name: {value, source, ...}}}
    calibration_history: list[dict] = Field(default_factory=list)
    
    def get_parameter(self, path: str) -> dict:
        """Get parameter by dot-notation path (e.g., 'kinetics.k_cat')."""
        keys = path.split(".")
        d = self.parameters
        for key in keys:
            d = d[key]
        return d


class UQResult(BaseModel):
    """Uncertainty quantification result."""
    model_config = {"frozen": True, "extra": "forbid"}
    
    id: UUID
    samples: list[list[float]] = Field(default_factory=list)
    statistics: dict[str, dict[str, float]] = Field(default_factory=dict)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    computation_time_s: float = 0.0
