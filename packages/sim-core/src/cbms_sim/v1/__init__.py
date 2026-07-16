"""
CBMS-Sim Public API v1.

This is the STABLE interface for downstream consumers (FastAPI, Celery, UI).
Breaking changes require a new major version (v2).
"""

from cbms_sim.v1.types import (
    SimulationRequest,
    SimulationResult,
    KineticsResult,
    MassBalanceResult,
    UQResult,
    BlockProperties,
    EconomicResult,
    ParameterSet,
    ParameterSetVersion,
    PlantProfile,
    ReagentFormulation,
    OperatingConditions,
    CaptureEfficiency,
    DistributionStats,
    Sensitivities,
    ComplianceFlags,
    SimulationOptions,
    SimulationType,
    CalciumSourceType,
    BoilerType,
    SimulationStatus,
)
from cbms_sim.v1.exceptions import (
    SimulationError,
    ValidationError,
    ConvergenceError,
    NumericalError,
    ParameterError,
    ResourceError,
    ErrorCode,
    ErrorContext,
)
from cbms_sim.v1.units import (
    # Unit conversions
    pascals_from_ppm,
    ppm_from_pascals,
    m3_per_hr_from_nm3_per_hr,
    kelvin_from_celsius,
    celsius_from_kelvin,
    # Unit constants
    STANDARD_TEMP_K,
    STANDARD_PRESSURE_PA,
    MOLAR_VOLUME_STP_M3_PER_MOL,
    # Validators
    assert_positive,
    assert_non_negative,
    assert_in_range,
)
from cbms_sim.v1.engine import SimulationEngine
from cbms_sim.v1.parameters import ParameterRegistry
from cbms_sim.v1.validators import (
    validate_simulation_request,
    validate_plant_profile,
    validate_reagent_formulation,
    validate_operating_conditions,
)

__version__ = "1.0.0"
__api_version__ = "v1"

__all__ = [
    # Version info
    "__version__",
    "__api_version__",
    # Types
    "SimulationRequest",
    "SimulationResult",
    "KineticsResult",
    "MassBalanceResult",
    "UQResult",
    "BlockProperties",
    "EconomicResult",
    "ParameterSet",
    "ParameterSetVersion",
    "PlantProfile",
    "ReagentFormulation",
    "OperatingConditions",
    "CaptureEfficiency",
    "DistributionStats",
    "Sensitivities",
    "ComplianceFlags",
    "SimulationOptions",
    "SimulationType",
    "CalciumSourceType",
    "BoilerType",
    "SimulationStatus",
    # Exceptions
    "SimulationError",
    "ValidationError",
    "ConvergenceError",
    "NumericalError",
    "ParameterError",
    "ResourceError",
    "ErrorCode",
    "ErrorContext",
    # Units
    "pascals_from_ppm",
    "ppm_from_pascals",
    "m3_per_hr_from_nm3_per_hr",
    "kelvin_from_celsius",
    "celsius_from_kelvin",
    "STANDARD_TEMP_K",
    "STANDARD_PRESSURE_PA",
    "MOLAR_VOLUME_STP_M3_PER_MOL",
    "assert_positive",
    "assert_non_negative",
    "assert_in_range",
    # Engine
    "SimulationEngine",
    "ParameterRegistry",
    # Validators
    "validate_simulation_request",
    "validate_plant_profile",
    "validate_reagent_formulation",
    "validate_operating_conditions",
]
