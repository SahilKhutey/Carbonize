"""Tests for the ParameterRegistry."""

import pytest
from cbms_sim.domain.parameters.registry import ParameterRegistry


def test_parameter_registry_loads(param_registry):
    assert param_registry.version == "2026.1"
    
    # Check that a known parameter exists
    k_cat_val = param_registry.get_value("kinetics.k_cat")
    assert k_cat_val == 1000000.0


def test_parameter_registry_key_error(param_registry):
    with pytest.raises(KeyError):
        param_registry.get("invalid.key")
