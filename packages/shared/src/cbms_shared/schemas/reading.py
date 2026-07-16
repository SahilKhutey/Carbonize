"""
Shared Pydantic schema for sensor readings.

USED BY:
- sim-core (when emitting synthetic data for validation)
- DAQ ingestion endpoint (when receiving real sensor data)
- Frontend validation dashboard (when displaying both)

This schema is the CONTRACT between physical and digital.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# =============================================================================
# ENUMS
# =============================================================================

class MeasurementType(str, Enum):
    """
    All measurement types in the system.
    
    MUST match the sensor inventory (Task 5.1).
    Adding a new type requires a migration.
    """
    # Liquid phase
    PH = "ph"
    CONDUCTIVITY = "conductivity"  # mS/cm
    TEMPERATURE = "temperature"      # °C
    DISSOLVED_OXYGEN = "dissolved_oxygen"  # mg/L
    DISSOLVED_CO2 = "dissolved_co2"  # mg/L
    DISSOLVED_SO2 = "dissolved_so2"  # mg/L
    ORP = "orp"  # mV
    TURBIDITY = "turbidity"  # NTU
    PH_DROP_RATE = "ph_drop_rate"  # pH/min (derived)
    
    # Gas phase
    CO2_GAS = "co2_gas"  # vol%
    SO2_GAS = "so2_gas"  # ppm
    NOX_GAS = "nox_gas"  # ppm
    GAS_FLOW = "gas_flow"  # Nm³/hr
    GAS_PRESSURE = "gas_pressure"  # mbar
    GAS_TEMPERATURE = "gas_temperature"  # °C
    PM_CONCENTRATION = "pm_concentration"  # mg/Nm³
    DIFFERENTIAL_PRESSURE = "differential_pressure"  # mbar (mesh)
    
    # Flow
    SLURRY_FLOW = "slurry_flow"  # L/min
    REAGENT_FLOW = "reagent_flow"  # L/min
    
    # Derived (computed from others)
    CO2_CAPTURE_RATE = "co2_capture_rate"  # % (derived)
    BLOCK_STRENGTH = "block_strength"  # MPa (lab measurement)
    CHITOSAN_CONCENTRATION = "chitosan_concentration"  # g/L


class DataSource(str, Enum):
    """Where did this measurement come from?"""
    SIMULATION = "simulation"  # From sim-core
    PHYSICAL_SENSOR = "physical_sensor"  # From real DAQ
    LAB_MEASUREMENT = "lab_measurement"  # From manual sampling
    CALCULATED = "calculated"  # Derived from other readings
    EXTERNAL_API = "external_api"  # Weather, market, etc.


class DataQuality(str, Enum):
    """Confidence in this measurement."""
    GOOD = "good"  # Normal operation, sensor calibrated
    DEGRADED = "degraded"  # Sensor drift, near calibration due
    SUSPECT = "suspect"  # Sensor flagged this as questionable
    CALIBRATING = "calibrating"  # Sensor in calibration mode
    OFFLINE = "offline"  # Sensor offline, value is last known
    MISSING = "missing"  # No reading available


class SensorHealth(str, Enum):
    """Overall sensor health."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAULT = "fault"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


# =============================================================================
# CORE MODELS
# =============================================================================

class Measurement(BaseModel):
    """
    A SINGLE measurement from a SINGLE sensor at a SINGLE point in time.
    
    This is the atomic unit of sensor data. Every reading, whether
    from a real DAQ or from sim-core, consists of one or more of these.
    """
    model_config = ConfigDict(
        extra="forbid",  # No extra fields — strict schema
        str_strip_whitespace=True,
        use_enum_values=True,
    )
    
    # REQUIRED
    measurement_type: MeasurementType
    value: float = Field(
        ...,
        description="The measured value (in the unit specified below)"
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unit of the value (e.g., 'pH', '°C', 'mg/L', '%')"
    )
    timestamp: datetime = Field(
        ...,
        description="When the measurement was taken (ISO 8601)"
    )
    
    # HIGHLY RECOMMENDED
    quality: DataQuality = DataQuality.GOOD
    sensor_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Physical or virtual sensor ID (e.g., 'pH_main_loop')"
    )
    
    # OPTIONAL
    quality_flags: list[str] = Field(
        default_factory=list,
        description="Specific quality issue codes (e.g., 'drift_high', 'noise_outlier')"
    )
    uncertainty: Optional[float] = Field(
        None,
        ge=0,
        description="1-sigma measurement uncertainty (in the same unit as value)"
    )
    raw_value: Optional[float] = Field(
        None,
        description="Pre-calibration value from sensor (for diagnostics)"
    )
    calibration_id: Optional[str] = Field(
        None,
        description="ID of the calibration record used for this measurement"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional sensor-specific metadata (e.g., ADC counts, raw voltage)"
    )
    
    @field_validator("timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (use UTC)")
        return v.astimezone(timezone.utc)
    
    @field_validator("value")
    @classmethod
    def check_finite(cls, v: float) -> float:
        import math
        if not math.isfinite(v):
            raise ValueError(f"value must be finite, got {v}")
        return v


class BatchMetadata(BaseModel):
    """
    Metadata about a BATCH of measurements (sent together).
    
    For DAQ: a single HTTP POST may contain multiple measurements
    from different sensors at the same time point.
    """
    model_config = ConfigDict(extra="forbid")
    
    source: DataSource
    source_version: str = Field(
        ...,
        description="Version of the source system (e.g., 'sim-core-0.3.1', 'daq-fw-2.4.0')"
    )
    
    # Optional context
    plant_id: Optional[UUID] = None
    simulation_id: Optional[UUID] = None
    run_id: Optional[UUID] = None
    experiment_id: Optional[str] = None
    
    # Quality of the batch
    is_calibration: bool = False
    is_test_data: bool = False
    
    # Schema versioning for forward compatibility
    schema_version: str = Field(default="1.0.0")
    
    extra: dict = Field(
        default_factory=dict,
        description="Additional metadata (operator, location, etc.)"
    )


class SensorReading(BaseModel):
    """
    A complete sensor reading: one or more measurements from one source.
    
    This is the TOP-LEVEL object for both ingestion AND emission.
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
    
    # Identification
    reading_id: UUID = Field(default_factory=uuid4)
    
    # When
    timestamp: datetime = Field(
        ...,
        description="When the readings were taken (ISO 8601, UTC)"
    )
    
    # What
    measurements: list[Measurement] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="One or more measurements in this reading"
    )
    
    # Context
    metadata: BatchMetadata
    
    # Health of the source sensor
    sensor_health: SensorHealth = SensorHealth.HEALTHY
    health_message: Optional[str] = None
    
    @field_validator("timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (use UTC)")
        return v.astimezone(timezone.utc)
    
    @model_validator(mode="after")
    def validate_measurement_consistency(self):
        """Cross-field validation: ensure measurements are consistent."""
        types_seen = set()
        for m in self.measurements:
            if m.measurement_type in types_seen:
                if not m.metadata.get("allow_duplicate"):
                    raise ValueError(
                        f"Duplicate measurement type: {m.measurement_type}. "
                        f"Group into one Measurement or mark allow_duplicate=true."
                    )
            types_seen.add(m.measurement_type)
        return self
    
    def get(self, measurement_type: MeasurementType) -> Optional[Measurement]:
        """Helper: get measurement by type."""
        for m in self.measurements:
            if m.measurement_type == measurement_type:
                return m
        return None
    
    def to_dict(self) -> dict:
        """Serialization helper."""
        return self.model_dump(mode="json", exclude_none=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "SensorReading":
        """Deserialization helper."""
        return cls(**data)


# =============================================================================
# SPECIALIZED EXTENSIONS (for specific use cases)
# =============================================================================

class SimulationReading(SensorReading):
    """
    Sensor reading from a simulation (sim-core output).
    """
    model_config = ConfigDict(extra="forbid")
    
    metadata: BatchMetadata = Field(
        default_factory=lambda: BatchMetadata(
            source=DataSource.SIMULATION,
            source_version="sim-core-unknown",
        )
    )
    simulation_id: UUID
    run_id: UUID
    timestep_seconds: float = Field(
        ...,
        ge=0,
        description="Simulation time (seconds) when this reading was taken"
    )


class SensorMaintenanceEvent(BaseModel):
    """Logged when a sensor is calibrated, cleaned, or replaced."""
    model_config = ConfigDict(extra="forbid")
    
    sensor_id: str
    event_type: Literal["calibration", "cleaning", "replacement", "fault", "recovery"]
    timestamp: datetime
    operator: str
    notes: Optional[str] = None
    pre_calibration_value: Optional[float] = None
    post_calibration_value: Optional[float] = None
    calibration_standard: Optional[str] = None
