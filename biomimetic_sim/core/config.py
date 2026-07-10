"""
core/config.py
Global physical constants, material properties, and tunable parameters
for the biomimetic multi-pollutant solidification system.
"""

from dataclasses import dataclass, field
from typing import Dict

# ============================================================
# PHYSICAL CONSTANTS
# ============================================================
R_GAS = 8.314                    # Universal gas constant [J/(mol·K)]
STD_TEMP = 273.15 + 25           # Standard temperature [K]
STD_PRESSURE = 101325.0          # Standard pressure [Pa]
AVOGADRO = 6.022e23              # Avogadro's number

# Molar masses [g/mol]
MOLAR = {
    "CO2":    44.01,
    "SO2":    64.07,
    "NO2":    46.01,
    "NO":     30.01,
    "CaCO3":  100.09,
    "CaSO4":  136.14,
    "CaSO3":  120.14,
    "CaOH2":  74.10,
    "H2O":    18.02,
    "CaCl2":  110.98,
    "Chitosan":  161.0,   # per monomer unit
}


# ============================================================
# REACTION KINETICS PARAMETERS
# ============================================================
@dataclass(frozen=True)
class KineticsConfig:
    """
    Tunable parameters for the enzymatic CO2 hydration model.
    Validated against: Mirjafari et al. 2007, Rigkos 2024.
    """
    # Carbonic anhydrase rate constants
    k_cat: float = 1.0e6          # Catalytic turnover [s^-1]
    K_M_co2: float = 8.5e-3       # Michaelis constant for CO2 [M]
    K_M_hco3: float = 26.0e-3     # Michaelis constant for HCO3- [M]
    k_inact: float = 5.0e-5      # Thermal inactivation rate at 40°C [s^-1]
    E_a_inact: float = 85.0e3    # Activation energy of inactivation [J/mol]

    # SO2 dissolution (pseudo-first-order in alkaline solution)
    k_so2_absorption: float = 2.5e-2  # Volumetric mass transfer coeff [m/s]

    # Chitosan gel transition threshold
    gel_critical_ph: float = 6.8
    gel_critical_viscosity: float = 1.2  # Pa·s

    # Heavy metal chelation
    k_chelation: float = 8.0e-3   # Effective chelation rate [m³/(mol·s)]


# ============================================================
# MATERIAL PROPERTY DATABASE
# ============================================================
@dataclass(frozen=True)
class MaterialLibrary:
    """
    Solid material database: density, compressive strength, leach rates.
    """
    # Pure mineralized outputs
    CACO3_DENSITY: float = 2710.0       # Calcite [kg/m³]
    CACO3_STRENGTH: float = 18.0        # MPa @ 48h curing

    GYPSUM_DENSITY: float = 2320.0      # kg/m³
    GYPSUM_STRENGTH: float = 4.0        # MPa (non-structural, filler only)

    CHITOSAN_DENSITY: float = 1400.0    # kg/m³ (dry film)
    CHITOSAN_TENSILE: float = 95.0      # MPa

    # Indian fly ash (Gondwana coal, post-ESP)
    FLY_ASH_DENSITY: float = 2300.0     # kg/m³
    FLY_ASH_POZZOLANICITY_INDEX: float = 0.85
    FLY_ASH_AVG_DIAMETER: float = 12.0  # microns

    # Composite block baseline (validated mix ratio)
    COMPOSITE_BASE_STRENGTH: float = 25.0  # MPa @ 48h, 200 bar
    COMPOSITE_DENSITY: float = 2100.0      # kg/m³

    # Regulatory thresholds
    CPCB_SO2_LIMIT: float = 200.0       # mg/Nm³ (Category C thermal)
    TCLP_LEACH_LIMIT_PB: float = 5.0   # mg/L (EPA 1311)
    TCLP_LEACH_LIMIT_HG: float = 0.2   # mg/L
    TCLP_LEACH_LIMIT_CD: float = 1.0   # mg/L


# ============================================================
# ECONOMIC INDICATORS (2026 INDIAN MARKET)
# ============================================================
@dataclass(frozen=True)
class EconomicConfig:
    """Live-tuned market rates. Refreshed nightly from CCTS feed."""
    CCTS_CARBON_PRICE_INR: float = 1850.0      # INR per tCO2 (2026 spot)
    BRICK_MARKET_PRICE_INR: float = 12.0        # INR per construction block
    ELECTRICITY_TARIFF_INR: float = 8.5         # INR per kWh (industrial HT)
    WATER_TARIFF_INR: float = 65.0             # INR per kL (industrial)
    CHITOSAN_FLAKE_PRICE_INR: float = 320.0    # INR per kg (coastal sourcing)
    CALCIUM_HYDROXIDE_PRICE_INR: float = 8500.0  # INR per ton
    STEEL_SLAG_PRICE_INR: float = 1200.0       # INR per ton (waste grade)
    DISCOUNT_RATE_ANNUAL: float = 0.11         # Indian industrial WACC


# ============================================================
# GEOMETRY / PROCESS DEFAULTS
# ============================================================
@dataclass(frozen=True)
class ReactorGeometry:
    """Default 10,000 Nm³/hr system dimensions."""
    TOWER_WIDTH: float = 2.5          # m (square cross-section)
    TOWER_HEIGHT: float = 12.0        # m
    GAS_VELOCITY: float = 0.44        # m/s (superficial)
    RESIDENCE_TIME: float = 27.0      # seconds
    LIQUID_TO_GAS_RATIO: float = 8.5  # L/Nm³
    MESH_COUNT: int = 6               # Number of static mesh layers
    MESH_PITCH_ANGLE: float = 30.0    # degrees (staggered)
    PRESS_FORCE: float = 200.0        # bar
    PRESS_DWELL_TIME: float = 60.0    # seconds


# ============================================================
# MASTER CONFIGURATION INSTANCE
# ============================================================
@dataclass(frozen=True)
class MasterConfig:
    kinetics: KineticsConfig = field(default_factory=KineticsConfig)
    materials: MaterialLibrary = field(default_factory=MaterialLibrary)
    economic: EconomicConfig = field(default_factory=EconomicConfig)
    geometry: ReactorGeometry = field(default_factory=ReactorGeometry)

    # Compile-time constants
    REGULATORY: Dict[str, float] = field(default_factory=lambda: {
        "CPCB_SO2_MAX": 200.0,
        "IS_2185_BLOCK_STRENGTH_MIN": 3.5,  # MPa (non-load-bearing)
        "IS_1077_BRICK_STRENGTH_MIN": 5.0,
    })


# Singleton accessor
CONFIG = MasterConfig()
