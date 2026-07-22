"""
Ingestion service: receives readings from real DAQ AND simulation,
stores them uniformly in the time-series database.
"""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Stubbed out imports assuming existence in the API package
try:
    from cbms_api.config import get_settings
    from cbms_api.db.connection import async_session_factory
    from cbms_api.db.models.sensor_reading import SensorReadingORM
except ImportError:
    pass

from cbms_shared.schemas.reading import (
    SensorReading, Measurement, BatchMetadata,
    DataSource, DataQuality,
)

class DummyLogger:
    def info(self, *args, **kwargs):
        pass

logger = DummyLogger()

class IngestionService:
    """Receives sensor readings from any source and persists them."""
    
    async def ingest(self, reading: SensorReading) -> dict:
        """
        Ingest a sensor reading into the time-series store.
        
        Both real sensor data and simulation output go through this method.
        """
        # 1. Validate
        self._validate(reading)
        
        # 2. Persist to time-series database
        async with async_session_factory() as session:
            # Each measurement is a separate row in TS
            for measurement in reading.measurements:
                await self._persist_measurement(
                    session=session,
                    reading=reading,
                    measurement=measurement,
                )
            await session.commit()
        
        # 3. Emit event for downstream consumers (WebSocket, alerts)
        await self._emit_event(reading)
        
        # 4. Return receipt
        receipt = {
            "reading_id": str(reading.reading_id),
            "ingested_count": len(reading.measurements),
            "ingested_at": datetime.now(UTC).isoformat(),
        }
        
        logger.info(
            "reading_ingested",
            reading_id=str(reading.reading_id),
            source=reading.metadata.source,
            count=len(reading.measurements),
            timestamp=reading.timestamp.isoformat(),
        )
        
        return receipt
    
    def _validate(self, reading: SensorReading) -> None:
        """Pre-ingestion validation."""
        now = datetime.now(UTC).replace(tzinfo=reading.timestamp.tzinfo)
        if reading.timestamp > now + timedelta(minutes=5):
            # Future timestamp within 5 min is OK (clock skew); more is suspect
            if reading.timestamp > now + timedelta(hours=1):
                raise ValueError(f"Timestamp {reading.timestamp} is too far in the future")
        
        if not reading.measurements:
            raise ValueError("Reading must have at least one measurement")
    
    async def _persist_measurement(
        self, session: AsyncSession,
        reading: SensorReading, measurement: Measurement,
    ) -> None:
        """Persist a single measurement to time-series store."""
        record = SensorReadingORM(
            reading_id=reading.reading_id,
            timestamp=reading.timestamp,
            measurement_type=measurement.measurement_type,
            value=measurement.value,
            unit=measurement.unit,
            quality=measurement.quality,
            sensor_id=measurement.sensor_id,
            uncertainty=measurement.uncertainty,
            source=reading.metadata.source,
            source_version=reading.metadata.source_version,
            plant_id=reading.metadata.plant_id,
            simulation_id=reading.metadata.simulation_id,
            extra_metadata=measurement.metadata,
        )
        session.add(record)
    
    async def _emit_event(self, reading: SensorReading) -> None:
        """Emit event for real-time consumers."""
        pass


ingestion_service = IngestionService()
