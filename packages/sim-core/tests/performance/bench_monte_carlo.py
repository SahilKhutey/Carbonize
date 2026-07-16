"""
Benchmarks for Monte Carlo UQ scaling and parallelization.
"""

import pytest
import numpy as np
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

from cbms_sim.domain.uq.monte_carlo import MonteCarloEngine
from cbms_sim.v1 import SimulationEngine, SimulationRequest, SimulationOptions, SimulationType
from cbms_sim.v1.types import PlantProfile, ReagentFormulation, OperatingConditions, BoilerType, CalciumSourceType
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone


def dummy_forward_model(params):
    """A dummy forward model that simulates computational cost."""
    # Run a busy loop to simulate CPU work
    x = 0.0
    for i in range(10000):
        x += np.sin(i) * np.cos(i)
    return x + sum(params)


class TestMonteCarloScaling:
    """How does MC scale with sample count and workers?"""
    
    @pytest.mark.parametrize("n_samples", [100, 500, 1000])
    def test_scaling_with_n_samples(self, n_samples, system_info, timer, result_collector):
        """
        BENCHMARK: How does wall time scale with N samples?
        """
        specs = {
            "param_0": {"type": "normal", "mean": 10.0, "std": 2.0},
            "param_1": {"type": "uniform", "min": 0.0, "max": 100.0},
        }
        
        mc = MonteCarloEngine(n_samples=n_samples, seed=42)
        
        with timer("mc_sampling") as t:
            samples = mc.generate_samples(specs)
            # Evaluate dummy forward model sequentially
            results = []
            for s in samples:
                results.append(dummy_forward_model(list(s.values())))
        
        time_per_sample_ms = t.elapsed_ms / n_samples
        
        metrics = {
            "n_samples": n_samples,
            "total_ms": t.elapsed * 1000,
            "time_per_sample_ms": time_per_sample_ms,
            "throughput_samples_per_sec": n_samples / t.elapsed,
        }
        
        result_collector.add(f"mc_samples_{n_samples}", metrics, system_info)
    
    @pytest.mark.parametrize("n_workers", [1, 2, 4])
    def test_parallel_scaling(self, n_workers, system_info, timer, result_collector):
        """
        BENCHMARK: How does wall time scale with N workers?
        """
        if n_workers > mp.cpu_count():
            pytest.skip(f"Only {mp.cpu_count()} CPUs available")
        
        n_samples = 1000
        mc = MonteCarloEngine(n_samples=n_samples, seed=42)
        specs = {
            "param_0": {"type": "normal", "mean": 10.0, "std": 2.0},
            "param_1": {"type": "uniform", "min": 0.0, "max": 100.0},
        }
        
        samples = mc.generate_samples(specs)
        sample_args = [list(s.values()) for s in samples]
        
        with timer("mc_parallel") as t:
            if n_workers == 1:
                results = [dummy_forward_model(args) for args in sample_args]
            else:
                with ProcessPoolExecutor(max_workers=n_workers) as executor:
                    results = list(executor.map(dummy_forward_model, sample_args, chunksize=100))
        
        metrics = {
            "n_workers": n_workers,
            "wall_time_s": t.elapsed,
            "samples_per_sec": n_samples / t.elapsed,
        }
        
        result_collector.add(f"mc_parallel_workers_{n_workers}", metrics, system_info)


class TestFullMonteCarloBenchmark:
    """End-to-end MC benchmark with realistic workload."""
    
    def test_full_mc_benchmark(
        self, warmed_engine, standard_plant, standard_reagent, standard_conditions,
        problem_size, system_info, timer, result_collector
    ):
        """
        BENCHMARK: Full MC pipeline at different problem sizes.
        """
        n_samples = problem_size["n_mc_samples"]
        expected_latency = problem_size["expected_latency_s"]
        
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
                simulation_type=SimulationType.MONTE_CARLO,
                n_mc_samples=n_samples,
            ),
            submitted_at=datetime.now(timezone.utc),
        )
        
        with timer("full_mc") as t:
            engine.run(request)
        
        metrics = {
            "problem_size_name": problem_size.get("name", "standard"),
            "n_samples": n_samples,
            "wall_time_s": t.elapsed,
            "throughput_samples_per_sec": n_samples / t.elapsed if t.elapsed > 0 else 0,
            "meets_target": t.elapsed <= expected_latency * 2.0,  # 2x threshold tolerance for slow environments
        }
        
        result_collector.add(f"full_mc_{n_samples}", metrics, system_info)
