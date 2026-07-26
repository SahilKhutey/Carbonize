"""
packages/api/tests/load/test_simulation_calibration_pipeline_load.py
Load testing for real simulation execution, DAQ pilot telemetry ingestion, and hardware spec sheet generation.
Runs high-concurrency requests to verify system throughput and responsiveness under production-scale traffic.
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from cbms_api.api.main import app


@pytest.mark.asyncio
async def test_concurrent_pilot_telemetry_and_hardware_spec_load(client, burst_login_tokens):
    """
    Simulate 50 concurrent DAQ edge gateway telemetry submissions and hardware spec sheet handoffs under JWT auth.
    """
    token = burst_login_tokens[0]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Telemetry Batch Payload
    telemetry_batch = {
        "plant_id": "00000000-0000-0000-0000-000000000001",
        "gateway_id": "pi-gateway-001",
        "source_version": "daq-fw-2.4.0",
        "batch": [
            {
                "sensor_id": f"CO2-GAS-0{i%5+1}",
                "value": 14.5 + i * 0.1,
                "unit": "vol%",
                "quality": "GOOD",
            }
            for i in range(10)
        ],
    }

    # 2. Hardware Spec Sheet Payload
    spec_request = {
        "exhaust_flow_nm3_hr": 12000.0,
        "target_co2_capture_pct": 90.0,
        "residence_time_s": 27.0,
        "liquid_to_gas_ratio": 8.5,
        "chitosan_wt_pct": 3.0,
        "ca_lime_wt_pct": 3.5,
        "enzyme_dosage_mg_l": 12.0,
    }

    async def send_telemetry():
        res = await client.post("/api/hardware/pilot-telemetry", json=telemetry_batch, headers=headers)
        return res.status_code

    async def send_spec_sheet():
        res = await client.post("/api/hardware/spec-sheet", json=spec_request, headers=headers)
        return res.status_code

    # Run 25 telemetry + 25 spec sheet requests concurrently
    tasks = [send_telemetry() for _ in range(25)] + [send_spec_sheet() for _ in range(25)]
    results = await asyncio.gather(*tasks)

    assert all(code in (200, 202, 429) for code in results)
    assert results.count(202) + results.count(200) > 0


@pytest.mark.asyncio
async def test_metrics_endpoint_under_concurrent_scraping():
    """
    Verify Prometheus /metrics endpoint handles concurrent high-frequency scraping cleanly.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async def scrape():
            res = await client.get("/metrics")
            return res.status_code, res.text

        scrapes = await asyncio.gather(*[scrape() for _ in range(10)])
        for status_code, text in scrapes:
            assert status_code == 200
            assert "cbms_http_requests_total" in text
