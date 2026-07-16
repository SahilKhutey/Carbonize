"""
Sensor data ingestion endpoint.

POST /api/v1/ingest        — Ingest one or more readings
POST /api/v1/ingest/batch  — Ingest many readings at once
GET  /api/v1/ingest/{id}    — Retrieve a specific reading
GET  /api/v1/ingest/recent  — Retrieve recent readings (for dashboard)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from datetime import datetime, timezone

from cbms_shared.schemas.reading import SensorReading, Measurement, BatchMetadata
from cbms_api.services.ingestion_service import ingestion_service

# Stub auth
def get_current_active_user():
    return {"user": "admin"}
AuthUser = Any

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_reading(
    reading: SensorReading,
    user: AuthUser = Depends(get_current_active_user),
):
    """
    Ingest a sensor reading.
    
    Accepts readings from:
    - Physical DAQ (DataSource.PHYSICAL_SENSOR)
    - Simulation (DataSource.SIMULATION)
    - Lab measurement (DataSource.LAB_MEASUREMENT)
    
    Returns: 201 Created with receipt
    """
    receipt = await ingestion_service.ingest(reading)
    return receipt

@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def ingest_batch(
    readings: List[SensorReading],
    user: AuthUser = Depends(get_current_active_user),
):
    """Ingest many readings at once (e.g., from a file upload)."""
    receipts = []
    for reading in readings:
        receipt = await ingestion_service.ingest(reading)
        receipts.append(receipt)
    return {"ingested": len(receipts), "receipts": receipts}

@router.get("/recent")
async def get_recent_readings(
    plant_id: str,
    measurement_type: str = None,
    limit: int = 100,
    user: AuthUser = Depends(get_current_active_user),
):
    """Retrieve recent readings for a plant (for dashboard)."""
    # Implementation: query TS DB
    pass
