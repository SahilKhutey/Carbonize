"""
packages/api/tests/integration/test_ingestion_api.py
Integration tests for sensor reading ingestion endpoints POST /api/ingest and POST /api/ingest/batch.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_ingest_single_reading(client, auth_a):
    """Test POST /api/ingest with valid SensorReading payload."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "reading_id": str(uuid4()),
        "timestamp": now_iso,
        "metadata": {
            "source": "physical_sensor",
            "source_version": "daq-fw-1.2.0",
        },
        "measurements": [
            {
                "measurement_type": "co2_gas",
                "value": 14.2,
                "unit": "vol%",
                "quality": "good",
                "sensor_id": "CO2-SENSOR-01",
                "timestamp": now_iso,
            }
        ],
    }

    response = await client.post("/api/ingest", json=payload, headers=auth_a)
    assert response.status_code == 201
    data = response.json()
    assert "reading_id" in data
    assert data["ingested_count"] == 1


@pytest.mark.asyncio
async def test_ingest_batch_readings(client, auth_a):
    """Test POST /api/ingest/batch with multiple readings."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = [
        {
            "reading_id": str(uuid4()),
            "timestamp": now_iso,
            "metadata": {
                "source": "physical_sensor",
                "source_version": "daq-fw-1.2.0",
            },
            "measurements": [
                {
                    "measurement_type": "temperature",
                    "value": 25.4,
                    "unit": "degC",
                    "quality": "good",
                    "sensor_id": "TEMP-01",
                    "timestamp": now_iso,
                }
            ],
        },
        {
            "reading_id": str(uuid4()),
            "timestamp": now_iso,
            "metadata": {
                "source": "lab_measurement",
                "source_version": "lab-manual-1.0.0",
            },
            "measurements": [
                {
                    "measurement_type": "ph",
                    "value": 8.5,
                    "unit": "pH",
                    "quality": "good",
                    "sensor_id": "PH-PROBE-02",
                    "timestamp": now_iso,
                }
            ],
        },
    ]

    response = await client.post("/api/ingest/batch", json=payload, headers=auth_a)
    assert response.status_code == 201
    data = response.json()
    assert data["ingested"] == 2
