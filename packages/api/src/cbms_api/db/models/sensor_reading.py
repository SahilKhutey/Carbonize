"""
SQLAlchemy model for sensor readings.
Single table for both real and simulated data.
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
import enum
from uuid import uuid4

# Stub Base
class Base:
    pass

class MeasurementTypeEnum(str, enum.Enum):
    """Same enum as in shared schema."""
    PH = "ph"
    CONDUCTIVITY = "conductivity"
    TEMPERATURE = "temperature"
    # Note: Full enum in cbms_shared.schemas.reading

class DataSourceEnum(str, enum.Enum):
    SIMULATION = "simulation"
    PHYSICAL_SENSOR = "physical_sensor"
    LAB_MEASUREMENT = "lab_measurement"
    CALCULATED = "calculated"

class SensorReadingORM(Base):
    """
    Time-series storage for all sensor readings.
    
    Same schema for real and simulated data.
    For high-throughput, consider TimescaleDB hypertable.
    """
    __tablename__ = "sensor_readings"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    reading_id = Column(PgUUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    measurement_type = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    quality = Column(String(20), default="good")
    sensor_id = Column(String(100), index=True)
    uncertainty = Column(Float, nullable=True)
    source = Column(String(50), nullable=False, index=True)
    source_version = Column(String(50), nullable=False)
    plant_id = Column(PgUUID(as_uuid=True), nullable=False, index=True)
    simulation_id = Column(PgUUID(as_uuid=True), nullable=True, index=True)
    extra_metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_readings_plant_time", "plant_id", "timestamp"),
        Index("ix_readings_type_time", "measurement_type", "timestamp"),
        Index("ix_readings_plant_type_time", "plant_id", "measurement_type", "timestamp"),
    )
