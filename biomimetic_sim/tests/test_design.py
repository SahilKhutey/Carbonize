"""
tests/test_design.py
Unit tests verifying the simulation request input hashing and caching design patterns.
"""

from api.routes.simulations import generate_input_hash

def test_input_hash_determinism():
    """Verify that identical inputs always map to the identical SHA-256 hash."""
    h1 = generate_input_hash(
        plant_profile_id="00000000-0000-0000-0000-000000000001",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        reactor_temperature_c=40.0
    )
    
    h2 = generate_input_hash(
        plant_profile_id="00000000-0000-0000-0000-000000000001",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        reactor_temperature_c=40.0
    )
    
    assert h1 == h2

def test_input_hash_differentiation():
    """Verify that different inputs map to different hashes."""
    h1 = generate_input_hash(
        plant_profile_id="00000000-0000-0000-0000-000000000001",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        reactor_temperature_c=40.0
    )
    
    # Different temperature
    h2 = generate_input_hash(
        plant_profile_id="00000000-0000-0000-0000-000000000001",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        reactor_temperature_c=45.0
    )
    
    # Different plant
    h3 = generate_input_hash(
        plant_profile_id="00000000-0000-0000-0000-000000000002",
        press_force_bar=200.0,
        enzyme_concentration_mg_l=12.0,
        chitosan_wt_pct=3.0,
        reactor_temperature_c=40.0
    )
    
    assert h1 != h2
    assert h1 != h3
