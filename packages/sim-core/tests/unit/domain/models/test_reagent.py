"""Tests for ReagentFormulation model."""

from decimal import Decimal
import pytest
from cbms_sim.domain.models.reagent import ReagentFormulation, CalciumSourceType


def test_reagent_formulation_valid(sample_reagent):
    assert sample_reagent.chitosan_wt_pct == Decimal("3.0")
    assert sample_reagent.ca_source_type == CalciumSourceType.LIME


def test_reagent_invalid_chitosan():
    with pytest.raises(ValueError, match="chitosan_wt_pct must be in"):
        ReagentFormulation(chitosan_wt_pct=Decimal("0.1"))


def test_reagent_invalid_ca():
    with pytest.raises(ValueError, match="ca_wt_pct must be in"):
        ReagentFormulation(ca_wt_pct=Decimal("15.0"))
