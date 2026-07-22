"""
Shared fixtures and configuration for performance benchmarks.
"""

import pytest
import time
import json
import platform
import psutil
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from cbms_sim.domain.kinetics import KineticsEngine
from cbms_sim.v1 import SimulationEngine, SimulationRequest
from cbms_sim.v1.parameters import ParameterRegistry


# =============================================================================
# HARDWARE PROFILING
# =============================================================================

@pytest.fixture(scope="session")
def system_info() -> dict:
    """Capture system info for benchmark context."""
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or "Unknown CPU",
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True),
        "memory_total_gb": psutil.virtual_memory().total / 1e9,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# PROBLEM SIZE FIXTURES (Realistic Reactor-Scale)
# =============================================================================

@pytest.fixture(params=[
    "small_industrial",  # Baseline
    "medium_industrial",  # Typical
    "large_industrial",   # Realistic large
    "very_large_industrial",  # Stress test
])
def problem_size(request):
    """Parametrized problem sizes for benchmark scaling."""
    sizes = {
        "small_industrial": {
            "exhaust_flow_nm3_hr": 5_000,
            "n_mc_samples": 100,  # Scaled down for faster test/benchmark feedback in suite run
            "description": "Small industry (food processing, light manufacturing)",
            "expected_latency_s": 1.0,
        },
        "medium_industrial": {
            "exhaust_flow_nm3_hr": 30_000,
            "n_mc_samples": 500,
            "description": "Medium industry (cement, steel, mid-size chemicals)",
            "expected_latency_s": 5.0,
        },
        "large_industrial": {
            "exhaust_flow_nm3_hr": 200_000,
            "n_mc_samples": 1000,
            "description": "Large industry (large power plant, refinery)",
            "expected_latency_s": 30.0,
        },
        "very_large_industrial": {
            "exhaust_flow_nm3_hr": 500_000,
            "n_mc_samples": 2000,
            "description": "Very large (utility-scale power, large refinery)",
            "expected_latency_s": 120.0,
        },
    }
    return sizes[request.param]


# =============================================================================
# REALISTIC INPUT FIXTURES
# =============================================================================

@pytest.fixture
def standard_plant():
    """Standard 10,000 Nm³/hr Indian coal plant."""
    from decimal import Decimal
    from cbms_sim.v1.types import PlantProfile, BoilerType
    from uuid import uuid4
    
    return PlantProfile(
        id=uuid4(),
        name="Standard Test Plant",
        location="Maharashtra",
        boiler_type=BoilerType.PULVERIZED_COAL,
        exhaust_flow_nm3_hr=Decimal("10000"),
        baseline_temperature_c=Decimal("150"),
        co2_vol_pct=Decimal("14"),
        so2_mg_per_nm3=Decimal("1200"),
        nox_mg_per_nm3=Decimal("500"),
        fly_ash_g_per_nm3=Decimal("45"),
        heavy_metal_profile=[],
        operating_hours_per_year=8000,
    )


@pytest.fixture
def standard_reagent():
    """Standard 3% chitosan formulation."""
    from decimal import Decimal
    from cbms_sim.v1.types import ReagentFormulation, CalciumSourceType
    from uuid import uuid4
    
    return ReagentFormulation(
        id=uuid4(),
        name="Standard 3% Chitosan",
        chitosan_wt_pct=Decimal("3.0"),
        ca_source_type=CalciumSourceType.LIME,
        ca_wt_pct=Decimal("3.5"),
        enzyme_mg_per_l=Decimal("12.0"),
        enzyme_type="bovine_CA",
    )


@pytest.fixture
def standard_conditions():
    """Standard operating conditions."""
    from decimal import Decimal
    from cbms_sim.v1.types import OperatingConditions
    
    return OperatingConditions(
        reactor_temp_c=Decimal("40"),
        pH_initial=Decimal("8.5"),
        liquid_to_gas_ratio=Decimal("8.5"),
        residence_time_s=Decimal("27"),
        mesh_count=6,
        press_force_bar=Decimal("200"),
        curing_temperature_c=Decimal("25"),
        curing_time_h=Decimal("48"),
    )


@pytest.fixture
def warmed_engine():
    """Kinetics engine with Numba kernels warmed up."""
    engine = KineticsEngine()
    engine.warmup()
    return engine


# =============================================================================
# TIMING UTILITIES
# =============================================================================

class Timer:
    """Context manager for timing with statistics."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
    
    @property
    def elapsed_ms(self) -> float:
        return self.elapsed * 1000
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "elapsed_s": self.elapsed,
            "elapsed_ms": self.elapsed * 1000,
        }


@pytest.fixture
def timer():
    """Provide a Timer instance for benchmarks."""
    return Timer


# =============================================================================
# RESULT STORAGE
# =============================================================================

class BenchmarkResultCollector:
    """Collect benchmark results for reporting."""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.results = []
    
    def add(self, name: str, metrics: dict, system_info: dict):
        self.results.append({
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "system": system_info,
        })
    
    def save(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        # Read existing file if present to merge results
        existing_data = {"results": []}
        if self.output_path.exists():
            try:
                with open(self.output_path, "r") as f:
                    existing_data = json.load(f)
            except Exception:
                pass
        
        merged_results = existing_data.get("results", [])
        # Overwrite or append based on uniqueness
        for new_r in self.results:
            # remove duplicates with same name
            merged_results = [r for r in merged_results if r["name"] != new_r["name"]]
            merged_results.append(new_r)
            
        with open(self.output_path, "w") as f:
            json.dump({"results": merged_results}, f, indent=2)


@pytest.fixture(scope="session")
def result_collector():
    output_path = Path("packages/sim-core/tests/performance/results/baseline.json")
    collector = BenchmarkResultCollector(output_path)
    yield collector
    collector.save()


def pytest_collection_modifyitems(config, items):
    """Automatically mark all benchmark tests in this folder as slow."""
    for item in items:
        if "performance" in str(getattr(item, "path", getattr(item, "fspath", ""))):
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.benchmark)
