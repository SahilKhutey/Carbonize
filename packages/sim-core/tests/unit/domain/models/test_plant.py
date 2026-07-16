"""Tests for PlantProfile model."""

from decimal import Decimal
import pytest
from cbms_sim.domain.models.plant import PlantProfile


def test_plant_profile_valid(sample_plant):
    assert sample_plant.name == "Standard Test Plant"
    assert sample_plant.exhaust_flow_nm3_hr == Decimal("10000.0")


def test_plant_profile_invalid_flow():
    with pytest.raises(ValueError, match="exhaust_flow_nm3_hr must be > 0"):
        PlantProfile(
            exhaust_flow_nm3_hr=Decimal("-10.0")
        )


def test_plant_profile_invalid_co2():
    with pytest.raises(ValueError, match="co2_vol_pct must be in"):
        PlantProfile(
            co2_vol_pct=Decimal("105.0")
        )
