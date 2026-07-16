"""
Benchmarks for the SimulationEngine (v1 public API).
"""

import pytest
import time
from cbms_sim.v1 import SimulationEngine, SimulationRequest, SimulationOptions, SimulationType
from cbms_sim.v1.types import PlantProfile, ReagentFormulation, OperatingConditions, BoilerType, CalciumSourceType
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone


class TestEngineThroughput:
    """Benchmark full request processing."""
    
    def test_engine_baseline_solve(
        self, warmed_engine, standard_plant, standard_reagent, standard_conditions,
        system_info, timer, result_collector
    ):
        """
        BENCHMARK: Time to process a single baseline simulation request.
        """
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        request = SimulationRequest(
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
        
        # Warmup
        engine.run(request)
        
        # Measure
        n_runs = 5
        times = []
        for _ in range(n_runs):
            with timer("engine_run") as t:
                engine.run(request)
            times.append(t.elapsed)
            
        mean_ms = sum(times) / len(times) * 1000
        
        metrics = {
            "mean_ms": mean_ms,
            "median_ms": sorted(times)[len(times)//2] * 1000,
            "n_runs": n_runs,
        }
        
        result_collector.add("engine_baseline_solve", metrics, system_info)
        
        assert mean_ms < 500, f"Full engine run mean latency {mean_ms:.1f}ms exceeds 500ms target"
