"""
tests/test_api_reagents.py
Unit tests verifying the reagents routing endpoints and costing functions.
"""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_reagent_lifecycle_endpoints():
    """Verify that reagents router successfully registers, calculates costs, and clones."""
    # 1. Cost calculation
    payload = {
        "name": "Standard Lime Chitosan",
        "description": "Feasibility formulation",
        "chitosan_wt_pct": 3.0,
        "ca_source_type": "Ca(OH)2",
        "ca_wt_pct": 3.5,
        "enzyme_type": "bovine_CA",
        "enzyme_mg_per_l": 12.0
    }
    response = client.post("/api/reagents/calculate-cost", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cost_per_kg_inr"] > 0.0
    assert "breakdown" in data
    
    # 2. Registration
    create_response = client.post("/api/reagents", json=payload)
    assert create_response.status_code == 201
    created_reagent = create_response.json()
    assert "id" in created_reagent
    reagent_id = created_reagent["id"]
    
    # 3. List
    list_response = client.get("/api/reagents")
    assert list_response.status_code == 200
    reagents_list = list_response.json()
    assert len(reagents_list) >= 1
    
    # 4. Fetch
    get_response = client.get(f"/api/reagents/{reagent_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Standard Lime Chitosan"
    
    # 5. Clone
    clone_response = client.post(f"/api/reagents/{reagent_id}/clone?new_name=Cloned%20Formulation")
    assert clone_response.status_code == 200
    cloned_reagent = clone_response.json()
    assert cloned_reagent["name"] == "Cloned Formulation"
    assert cloned_reagent["id"] != reagent_id
