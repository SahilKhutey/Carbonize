"""Tests for OperatingConditions model."""

from decimal import Decimal
import pytest
from cbms_sim.domain.models.conditions import OperatingConditions


def test_conditions_valid(sample_conditions):
    assert sample_conditions.reactor_temp_c == Decimal("40.0")


def test_conditions_invalid_temp():
    with pytest.raises(ValueError, match="reactor_temp_c must be in"):
        OperatingConditions(reactor_temp_c=Decimal("15.0"))


def test_conditions_invalid_lg():
    with pytest.raises(ValueError, match="L/G ratio must be in"):
        OperatingConditions(liquid_to_gas_ratio=Decimal("25.0"))


def test_conditions_invalid_press():
    with pytest.raises(ValueError, match="press_force_bar must be in"):
        OperatingConditions(press_force_bar=Decimal("600.0"))
