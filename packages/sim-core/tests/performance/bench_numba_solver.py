"""
Benchmarks for the Numba-compiled ODE solver.

Establishes baseline performance for production sizing.
"""

import pytest
import numpy as np
import time
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba
from cbms_sim.domain.kinetics.engine import KineticsEngine
from cbms_sim.v1.types import (
    PlantProfile, ReagentFormulation, OperatingConditions,
    BoilerType, CalciumSourceType
)
from uuid import uuid4
from decimal import Decimal


# =============================================================================
# BASELINE: Single ODE solve (warm Numba)
# =============================================================================

class TestSingleSolve:
    """Baseline: single deterministic solve."""
    
    def test_single_solve_warm(
        self, warmed_engine, standard_plant, standard_reagent, standard_conditions,
        system_info, timer, result_collector
    ):
        """
        BENCHMARK: Single ODE solve after Numba warmup.
        
        DoD target: < 200ms for standard conditions.
        """
        # Warm up
        warmed_engine.solve(
            standard_plant, standard_reagent, standard_conditions
        )
        
        # Measure
        n_runs = 10
        times = []
        for _ in range(n_runs):
            with timer("single_solve") as t:
                warmed_engine.solve(
                    standard_plant, standard_reagent, standard_conditions
                )
            times.append(t.elapsed)
        
        mean_ms = np.mean(times) * 1000
        median_ms = np.median(times) * 1000
        p95_ms = np.percentile(times, 95) * 1000
        
        metrics = {
            "n_runs": n_runs,
            "mean_ms": mean_ms,
            "median_ms": median_ms,
            "p95_ms": p95_ms,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "std_ms": np.std(times) * 1000,
        }
        
        result_collector.add("single_solve_warm", metrics, system_info)
        
        # DoD: < 200ms p95 for single solve
        assert p95_ms < 200, \
            f"p95 latency {p95_ms:.1f}ms exceeds 200ms target"
        
    def test_cold_start_includes_warmup(self, system_info, timer, result_collector):
        """
        BENCHMARK: First-ever solve includes Numba JIT compilation.
        """
        engine = KineticsEngine()
        
        plant = PlantProfile(
            id=uuid4(), name="x", location="x", boiler_type=BoilerType.PULVERIZED_COAL,
            exhaust_flow_nm3_hr=Decimal("10000"),
            baseline_temperature_c=Decimal("150"),
            co2_vol_pct=Decimal("14"),
            so2_mg_per_nm3=Decimal("1200"),
            nox_mg_per_nm3=Decimal("500"),
            fly_ash_g_per_nm3=Decimal("45"),
        )
        reagent = ReagentFormulation(
            id=uuid4(), name="x",
            chitosan_wt_pct=Decimal("3.0"),
            ca_source_type=CalciumSourceType.LIME,
            ca_wt_pct=Decimal("3.5"),
            enzyme_mg_per_l=Decimal("12.0"),
        )
        conditions = OperatingConditions(
            reactor_temp_c=Decimal("40"),
            pH_initial=Decimal("8.5"),
            liquid_to_gas_ratio=Decimal("8.5"),
            residence_time_s=Decimal("27"),
        )
        
        with timer("cold_start") as t:
            engine.solve(plant, reagent, conditions)
        
        metrics = {
            "cold_start_ms": t.elapsed * 1000,
            "includes_compilation": True,
            "note": "One-time cost; subsequent calls are < 200ms",
        }
        
        result_collector.add("cold_start_includes_warmup", metrics, system_info)
        
        # Cold start should be < 5s (very generous)
        assert t.elapsed < 5.0, f"Cold start {t.elapsed:.2f}s exceeds 5s"


# =============================================================================
# SCALING: Problem size impact
# =============================================================================

class TestScaling:
    """How does performance scale with problem size?"""
    
    @pytest.mark.parametrize("flow_rate", [
        1_000, 10_000, 100_000, 500_000
    ])
    def test_scaling_with_flow_rate(
        self, warmed_engine, flow_rate, system_info, timer, result_collector
    ):
        """
        BENCHMARK: How does solve time scale with plant size?
        """
        plant = PlantProfile(
            id=uuid4(), name="x", location="x", boiler_type=BoilerType.PULVERIZED_COAL,
            exhaust_flow_nm3_hr=Decimal(str(flow_rate)),
            baseline_temperature_c=Decimal("150"),
            co2_vol_pct=Decimal("14"),
            so2_mg_per_nm3=Decimal("1200"),
            nox_mg_per_nm3=Decimal("500"),
            fly_ash_g_per_nm3=Decimal("45"),
        )
        reagent = ReagentFormulation(
            id=uuid4(), name="x",
            chitosan_wt_pct=Decimal("3.0"),
            ca_source_type=CalciumSourceType.LIME,
            ca_wt_pct=Decimal("3.5"),
            enzyme_mg_per_l=Decimal("12.0"),
        )
        conditions = OperatingConditions(
            reactor_temp_c=Decimal("40"),
            pH_initial=Decimal("8.5"),
            liquid_to_gas_ratio=Decimal("8.5"),
            residence_time_s=Decimal("27"),
        )
        
        # Warmup
        warmed_engine.solve(plant, reagent, conditions)
        
        # Measure
        n_runs = 5
        times = []
        for _ in range(n_runs):
            with timer("solve") as t:
                warmed_engine.solve(plant, reagent, conditions)
            times.append(t.elapsed)
        
        mean_ms = np.mean(times) * 1000
        
        metrics = {
            "flow_rate": flow_rate,
            "mean_ms": mean_ms,
            "median_ms": np.median(times) * 1000,
        }
        
        result_collector.add(f"scaling_flow_{flow_rate}", metrics, system_info)
        
        assert mean_ms < 500, \
            f"Flow={flow_rate}: {mean_ms:.1f}ms exceeds 500ms"


# =============================================================================
# BOTTLENECK IDENTIFICATION: Profile the solve
# =============================================================================

class TestBottleneckIdentification:
    """Profile where time is spent in the solve pipeline."""
    
    def test_time_breakdown(
        self, warmed_engine, standard_plant, standard_reagent, standard_conditions,
        system_info, timer, result_collector
    ):
        """
        BENCHMARK: Breakdown of time spent in each phase.
        """
        # Warmup
        warmed_engine.solve(standard_plant, standard_reagent, standard_conditions)
        
        # Phase 1: Initial conditions
        with timer("init_conditions") as t_init:
            for _ in range(100):
                y0 = warmed_engine._compute_initial_conditions(
                    standard_plant, standard_reagent, standard_conditions
                )
        init_per_call = t_init.elapsed_ms / 100
        
        # Phase 2: RHS evaluation (kernel)
        params = {
            "k_cat": 1.0e6,
            "K_M_co2": 8.5e-3,
            "k_inact": 5.0e-5,
            "E_a_inact": 85.0e3,
            "k_so2": 2.5e-2,
            "k_chel": 8.0e-3,
            "ca_cl2": float(y0[2]),
            "pH_initial": float(standard_conditions.pH_initial),
            "T_reactor": float(standard_conditions.reactor_temp_c) + 273.15,
        }
        y = y0.copy()
        with timer("rhs_eval") as t_rhs:
            for _ in range(10000):
                result = reaction_rhs_numba(0.0, y, **params)
        rhs_per_call_us = t_rhs.elapsed_ms * 1000 / 10000
        
        # Phase 3: Full solve
        with timer("full_solve") as t_full:
            for _ in range(10):
                warmed_engine.solve(standard_plant, standard_reagent, standard_conditions)
        solve_per_call = t_full.elapsed_ms / 10
        
        estimated_rhs_per_solve = 300
        estimated_rhs_time = (rhs_per_call_us / 1000) * estimated_rhs_per_solve
        
        metrics = {
            "init_conditions_per_call_ms": init_per_call,
            "rhs_eval_per_call_us": rhs_per_call_us,
            "full_solve_per_call_ms": solve_per_call,
            "estimated_rhs_evals_per_solve": estimated_rhs_per_solve,
            "estimated_rhs_time_per_solve_ms": estimated_rhs_time,
            "estimated_solver_overhead_ms": solve_per_call - estimated_rhs_time,
        }
        
        result_collector.add("solver_time_breakdown", metrics, system_info)


# =============================================================================
# NUMBA COMPILATION OVERHEAD
# =============================================================================

class TestNumbaCompilation:
    """Measure Numba JIT compilation cost."""
    
    def test_first_call_vs_cached(self, system_info, timer, result_collector):
        """
        BENCHMARK: Compare first call vs cached call (AOT/JIT cache).
        """
        # Re-import to guarantee no local compilation
        y = np.array([10.0, 1.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        params = {
            "k_cat": 1e6, "K_M_co2": 8.5e-3,
            "k_inact": 5e-5, "E_a_inact": 85e3,
            "k_so2": 2.5e-2, "k_chel": 8e-3,
            "ca_cl2": 6.75, "pH_initial": 8.5, "T_reactor": 313.15,
        }
        
        # JIT warm-up triggers:
        # First call (cold) - reaction_rhs_numba should already be compiled if conftest or warm solves ran
        # But let's check caching overhead by running it repeatedly.
        with timer("cached_call_first") as t1:
            reaction_rhs_numba(0.0, y, **params)
            
        with timer("cached_call_second") as t2:
            for _ in range(1000):
                reaction_rhs_numba(0.0, y, **params)
        
        metrics = {
            "single_numba_call_ms": t1.elapsed_ms,
            "thousand_numba_calls_ms": t2.elapsed_ms,
            "average_numba_call_us": t2.elapsed_ms * 1000 / 1000,
        }
        
        result_collector.add("numba_compilation_and_cache", metrics, system_info)
