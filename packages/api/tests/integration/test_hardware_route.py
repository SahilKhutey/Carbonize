"""
Integration tests for /api/v1/hardware/spec-sheet endpoint.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from cbms_api.api.main import app
from cbms_api.api.dependencies import get_active_tenant_id


@pytest.fixture(autouse=True)
def override_tenant():
    dummy_org_id = uuid4()
    app.dependency_overrides[get_active_tenant_id] = lambda: dummy_org_id
    yield
    app.dependency_overrides.pop(get_active_tenant_id, None)


@pytest.mark.anyio
async def test_generate_hardware_spec_sheet_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "exhaust_flow_nm3_hr": 12000.0,
            "target_co2_capture_pct": 85.0,
            "residence_time_s": 30.0,
            "liquid_to_gas_ratio": 9.0,
            "chitosan_wt_pct": 3.0,
            "ca_lime_wt_pct": 3.5,
            "enzyme_dosage_mg_l": 15.0,
            "comparator_result": {
                "status": "VALIDATED",
                "within_90pct_ci_pct": 90.0,
            },
            "provenance_status": "🟢 Bench-validated"
        }
        res = await ac.post("/api/hardware/spec-sheet", json=payload)
        
        assert res.status_code == 200
        data = res.json()
        
        assert data["target_flue_gas_flow_nm3_hr"] == 12000.0
        assert data["applied_safety_margin_pct"] == 15.0
        assert data["sized_reactor_volume_m3"] > data["reactor_volume_m3"]
        assert data["trust_score"]["trust_level"] == "HIGH_CONFIDENCE_VALIDATED"
        assert "chitosan_consumption_kg_per_day" in data


@pytest.mark.anyio
async def test_export_hardware_spec_markdown_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "exhaust_flow_nm3_hr": 10000.0,
            "target_co2_capture_pct": 85.0,
            "residence_time_s": 27.0,
        }
        res = await ac.post("/api/hardware/spec-sheet/export-markdown", json=payload)
        
        assert res.status_code == 200
        text = res.text
        assert "# 🏗️ Hardware Procurement Specification Sheet" in text
        assert "Primary Reactor Column Geometry" in text
        assert "24-Hour Consumables & Chemical Feed Schedule" in text
