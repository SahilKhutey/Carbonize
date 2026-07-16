"""
Benchmarks for I/O overhead: registry loading and model serialization.
"""

import pytest
import json
from cbms_sim.v1.parameters import ParameterRegistry
from cbms_sim.v1 import SimulationRequest, SimulationOptions, SimulationType
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone


class TestIOOverhead:
    """Benchmark serialization and file I/O operations."""
    
    def test_registry_loading_overhead(self, system_info, timer, result_collector):
        """
        BENCHMARK: Time to load parameter sets from registry.
        """
        n_loads = 50
        with timer("registry_load") as t:
            for _ in range(n_loads):
                registry = ParameterRegistry.from_version("v2026.1")
                
        metrics = {
            "n_loads": n_loads,
            "total_ms": t.elapsed_ms,
            "average_load_ms": t.elapsed_ms / n_loads,
        }
        
        result_collector.add("registry_loading_overhead", metrics, system_info)
        
    def test_json_serialization_overhead(self, standard_plant, standard_reagent, standard_conditions, system_info, timer, result_collector):
        """
        BENCHMARK: Pydantic v2 dump_json and model_validate overhead.
        """
        req = SimulationRequest(
            request_id=uuid4(),
            org_id=uuid4(),
            user_id=uuid4(),
            plant=standard_plant,
            reagent=standard_reagent,
            conditions=standard_conditions,
            options=SimulationOptions(
                simulation_type=SimulationType.BASELINE,
                n_mc_samples=100,
            ),
            submitted_at=datetime.now(timezone.utc),
        )
        
        n_iters = 1000
        
        # Serialize to JSON
        with timer("serialize") as t_ser:
            for _ in range(n_iters):
                json_str = req.model_dump_json()
                
        # Deserialize from JSON
        with timer("deserialize") as t_deser:
            for _ in range(n_iters):
                SimulationRequest.model_validate_json(json_str)
                
        metrics = {
            "n_iterations": n_iters,
            "serialize_per_call_us": t_ser.elapsed_ms * 1000 / n_iters,
            "deserialize_per_call_us": t_deser.elapsed_ms * 1000 / n_iters,
        }
        
        result_collector.add("json_serialization_overhead", metrics, system_info)
