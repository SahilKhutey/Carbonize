"""
Benchmarks for ODE solver convergence scaling (accuracy vs speed).
"""

import pytest
import numpy as np
from cbms_sim.domain.kinetics.engine import KineticsEngine, KineticsConfig


class TestConvergenceScaling:
    """Benchmark how solver tolerances affect solve time and steps."""
    
    @pytest.mark.parametrize("tol", [
        (1e-4, 1e-6),
        (1e-6, 1e-8),
        (1e-8, 1e-10),
        (1e-10, 1e-12),
    ])
    def test_tolerance_scaling(
        self, tol, standard_plant, standard_reagent, standard_conditions,
        system_info, timer, result_collector
    ):
        """
        BENCHMARK: Impact of rtol/atol on solve time and step count.
        """
        rtol, atol = tol
        config = KineticsConfig(rtol=rtol, atol=atol)
        engine = KineticsEngine(config=config)
        engine.warmup()
        
        # Warm run
        engine.solve(standard_plant, standard_reagent, standard_conditions)
        
        # Measure
        n_runs = 5
        times = []
        for _ in range(n_runs):
            with timer("solve") as t:
                res = engine.solve(standard_plant, standard_reagent, standard_conditions)
            times.append(t.elapsed)
            
        mean_ms = np.mean(times) * 1000
        nfev = res.diagnostics.get("nfev", 0)
        njev = res.diagnostics.get("njev", 0)
        
        metrics = {
            "rtol": rtol,
            "atol": atol,
            "mean_ms": mean_ms,
            "nfev": nfev,
            "njev": njev,
        }
        
        result_collector.add(f"tolerance_rtol_{rtol}", metrics, system_info)
