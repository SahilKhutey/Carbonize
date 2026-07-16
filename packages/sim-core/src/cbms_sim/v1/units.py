"""
Unit conversion helpers for the v1 API boundary.

All conversions are explicit and named. No implicit conversions happen
inside sim-core — callers must convert at the API boundary.
"""

from decimal import Decimal

# Physical constants
STANDARD_TEMP_K = 273.15 + 25       # 298.15 K (25°C)
STANDARD_PRESSURE_PA = 101325.0    # 1 atm
MOLAR_VOLUME_STP_M3_PER_MOL = 0.022414  # At STP


# =============================================================================
# PRESSURE / CONCENTRATION CONVERSIONS
# =============================================================================

def pascals_from_ppm(
    ppm: float,
    molecular_weight_g_per_mol: float,
    temperature_k: float = STANDARD_TEMP_K,
    pressure_pa: float = STANDARD_PRESSURE_PA,
) -> float:
    """
    Convert gas concentration from ppm (by volume) to Pa (partial pressure).
    """
    if ppm < 0:
        raise ValueError(f"ppm must be non-negative, got {ppm}")
    mole_fraction = ppm * 1e-6
    return mole_fraction * pressure_pa


def ppm_from_pascals(
    pa: float,
    temperature_k: float = STANDARD_TEMP_K,
    pressure_pa: float = STANDARD_PRESSURE_PA,
) -> float:
    """
    Convert partial pressure (Pa) to ppm (by volume).
    """
    if pa < 0:
        raise ValueError(f"Pa must be non-negative, got {pa}")
    mole_fraction = pa / pressure_pa
    return mole_fraction * 1e6


# =============================================================================
# FLOW CONVERSIONS
# =============================================================================

def m3_per_hr_from_nm3_per_hr(
    flow_nm3_per_hr: float,
    temperature_k: float,
    pressure_pa: float = STANDARD_PRESSURE_PA,
) -> float:
    """
    Convert normal m³/hr (at STP) to actual m³/hr at process conditions.
    """
    if flow_nm3_per_hr < 0:
        raise ValueError(f"Flow must be non-negative, got {flow_nm3_per_hr}")
    return flow_nm3_per_hr * (STANDARD_TEMP_K / temperature_k) * (pressure_pa / STANDARD_PRESSURE_PA)


# =============================================================================
# TEMPERATURE CONVERSIONS
# =============================================================================

def kelvin_from_celsius(celsius: float) -> float:
    """Convert °C to K. No validation (allows negative for physics)."""
    return celsius + 273.15


def celsius_from_kelvin(kelvin: float) -> float:
    """Convert K to °C."""
    if kelvin < 0:
        raise ValueError(f"Kelvin cannot be negative, got {kelvin}")
    return kelvin - 273.15


# =============================================================================
# VALIDATION HELPERS (for use in custom validators)
# =============================================================================

def assert_positive(value: float, name: str = "value") -> None:
    """Assert value > 0."""
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def assert_non_negative(value: float, name: str = "value") -> None:
    """Assert value >= 0."""
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def assert_in_range(value: float, min_val: float, max_val: float, name: str = "value") -> None:
    """Assert min <= value <= max."""
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} must be in [{min_val}, {max_val}], got {value}")
