"""
Property-based tests for the SimulationEngine (v1 API).
"""

import pytest
import json
from hypothesis import given
from cbms_sim.v1 import (
    SimulationEngine, SimulationRequest, SimulationResult,
    SimulationStatus, SimulationError, ValidationError,
    ConvergenceError,
)
from .conftest import ci_settings
from .strategies import simulation_request_strategy


class TestEngineProperties:
    """Properties that must hold for the v1 public API engine."""
    
    @given(request=simulation_request_strategy())
    @ci_settings
    def test_engine_never_crashes(self, request):
        """
        PROPERTY: For any valid SimulationRequest, the engine should
        either succeed or raise a specific SimulationError subclass.
        """
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        try:
            result = engine.run(request)
            assert isinstance(result, SimulationResult)
        except (ValidationError, ConvergenceError, SimulationError):
            pass
        except Exception as e:
            pytest.fail(
                f"Engine raised generic exception ({type(e).__name__}): {e}. "
                f"Input: {request.model_dump()}"
            )
            
    @given(request=simulation_request_strategy())
    @ci_settings
    def test_successful_result_is_valid(self, request):
        """
        PROPERTY: If the engine succeeds, the result must be completed
        and JSON-serializable.
        """
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        try:
            result = engine.run(request)
        except (ValidationError, ConvergenceError, SimulationError):
            return
            
        assert result.status == SimulationStatus.COMPLETED
        assert result.output_hash is not None
        assert result.output_hash != ""
        
        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        
    @given(request=simulation_request_strategy())
    @ci_settings
    def test_capture_rates_in_valid_range(self, request):
        """
        PROPERTY: Capture rates in a successful result must be in [0, 100]%.
        """
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        try:
            result = engine.run(request)
        except (ValidationError, ConvergenceError, SimulationError):
            return
            
        if result.kinetics and result.kinetics.capture:
            assert 0 <= result.kinetics.capture.co2_pct <= 100
            assert 0 <= result.kinetics.capture.so2_pct <= 100
            assert 0 <= result.kinetics.capture.pm_pct <= 100
            assert 0 <= result.kinetics.capture.metal_pct <= 100
            
    @given(request=simulation_request_strategy())
    @ci_settings
    def test_engine_deterministic(self, request):
        """
        PROPERTY: Same request run twice → same output_hash.
        """
        options_updated = request.options.model_copy(update={"random_seed": 42})
        request_updated = request.model_copy(update={"options": options_updated})
        
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        try:
            r1 = engine.run(request_updated)
            r2 = engine.run(request_updated)
            assert r1.output_hash == r2.output_hash
        except (ValidationError, ConvergenceError, SimulationError):
            pass
