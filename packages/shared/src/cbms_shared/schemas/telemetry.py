"""
Telemetry schemas for PLC/DAQ edge ingestion and held-out pilot dataset evaluation.
Matches hardware/software-daq-edge-cloud.md specification.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class TelemetryPoint(BaseModel):
    """Single sensor telemetry point from PLC/DAQ gateway."""
    ts: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of observation")
    sensor_id: str = Field(..., json_schema_extra={"example": "CO2-GAS-01"}, description="Unique sensor tag")
    value: float = Field(..., description="Scaled process value in engineering units")
    unit: str = Field(..., json_schema_extra={"example": "vol%"}, description="Engineering unit")
    quality: Literal["GOOD", "UNCERTAIN", "BAD_RANGE", "BAD_STUCK"] = Field(default="GOOD", description="Quality code")
    raw_counts: Optional[int] = Field(None, description="Raw 4-20mA / Modbus ADC counts")
    cal_offset: float = Field(default=0.0, description="Applied calibration offset")
    cal_slope: float = Field(default=1.0, description="Applied calibration slope")


class TelemetryBatch(BaseModel):
    """Batched sensor telemetry payload from edge gateway (POST /api/v1/hardware/pilot-telemetry)."""
    plant_id: str = Field(..., description="Plant identifier UUID")
    gateway_id: str = Field(default="pi-gateway-001", description="Edge gateway identifier")
    source_version: str = Field(default="daq-fw-2.4.0", description="DAQ firmware version")
    batch: List[TelemetryPoint] = Field(..., description="Array of up to 500 telemetry points")


class PilotTelemetryIngestionResult(BaseModel):
    """Response payload for telemetry ingestion endpoint."""
    batch_id: UUID = Field(default_factory=uuid4)
    processed_count: int
    quality_summary: dict[str, int]
    status: str = "ACCEPTED"
    held_out_comparison_queued: bool = True
