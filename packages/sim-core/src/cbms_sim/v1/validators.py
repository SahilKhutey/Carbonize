"""
Input validation functions for v1 API.
"""

from typing import Any
from cbms_sim.v1.types import SimulationRequest, PlantProfile, ReagentFormulation, OperatingConditions
from cbms_sim.v1.exceptions import ValidationError

def validate_simulation_request(data: Any) -> SimulationRequest:
    try:
        if isinstance(data, dict):
            return SimulationRequest.model_validate(data)
        elif isinstance(data, SimulationRequest):
            return data
        else:
            raise TypeError("Expected dict or SimulationRequest")
    except Exception as e:
        raise ValidationError(f"Invalid simulation request: {e}") from e

def validate_plant_profile(data: Any) -> PlantProfile:
    try:
        if isinstance(data, dict):
            return PlantProfile.model_validate(data)
        elif isinstance(data, PlantProfile):
            return data
        else:
            raise TypeError("Expected dict or PlantProfile")
    except Exception as e:
        raise ValidationError(f"Invalid plant profile: {e}") from e

def validate_reagent_formulation(data: Any) -> ReagentFormulation:
    try:
        if isinstance(data, dict):
            return ReagentFormulation.model_validate(data)
        elif isinstance(data, ReagentFormulation):
            return data
        else:
            raise TypeError("Expected dict or ReagentFormulation")
    except Exception as e:
        raise ValidationError(f"Invalid reagent formulation: {e}") from e

def validate_operating_conditions(data: Any) -> OperatingConditions:
    try:
        if isinstance(data, dict):
            return OperatingConditions.model_validate(data)
        elif isinstance(data, OperatingConditions):
            return data
        else:
            raise TypeError("Expected dict or OperatingConditions")
    except Exception as e:
        raise ValidationError(f"Invalid operating conditions: {e}") from e
