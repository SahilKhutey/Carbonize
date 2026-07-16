"""
Benchmarks for concurrency and multithreading throughput.
"""

import pytest
import concurrent.futures
from cbms_sim.v1 import SimulationEngine, SimulationRequest, SimulationOptions, SimulationType
from cbms_sim.v1.types import PlantProfile, ReagentFormulation, OperatingConditions, BoilerType, CalciumSourceType
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone


class TestConcurrentSimulation:
    """Benchmark engine performance under concurrent loads."""
    
    def test_concurrent_throughput(self, standard_plant, standard_reagent, standard_conditions, system_info, timer, result_collector):
        """
        BENCHMARK: Concurrent batch processing throughput.
        """
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        # Create a batch of baseline requests
        batch = []
        for _ in range(10):
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
            batch.append(req)
            
        # Serial run
        with timer("serial") as t_serial:
            for req in batch:
                engine.run(req)
                
        # Concurrent run (using ThreadPoolExecutor)
        with timer("concurrent") as t_parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                list(executor.map(engine.run, batch))
                
        speedup = t_serial.elapsed / t_parallel.elapsed if t_parallel.elapsed > 0 else 0
        
        metrics = {
            "batch_size": len(batch),
            "serial_time_s": t_serial.elapsed,
            "parallel_time_s": t_parallel.elapsed,
            "speedup": speedup,
            "throughput_per_sec_serial": len(batch) / t_serial.elapsed if t_serial.elapsed > 0 else 0,
            "throughput_per_sec_parallel": len(batch) / t_parallel.elapsed if t_parallel.elapsed > 0 else 0,
        }
        
        result_collector.add("concurrent_throughput", metrics, system_info)
