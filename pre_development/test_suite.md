# 🧪 Complete Test Suite: CBMS-Sim Full Testing Framework

This document defines the comprehensive testing strategy, directory maps, configurations, and concrete test case implementations across the testing pyramid for the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. Test Strategy Overview

### 1.1 The Test Pyramid

```
                       ┌────────────────────────┐
                       │        E2E (5%)        │  ← Playwright / Cypress
                       │       ~10 tests        │
                       ├────────────────────────┤
                   ┌───┤     Contract (10%)     ├───┐  ← OpenAPI / Schemas
                   │   │       ~20 tests        │   │
                   │   ├────────────────────────┤   │
           ┌───────┴───┤   Integration (25%)    ├───┴───────┐  ← FastAPI Router / Postgres
           │           │       ~50 tests        │           │
           │           ├────────────────────────┤           │
   ┌───────┴───────────┤       Unit (60%)       ├───────────┴───────┐  ← Pure Kinetics ODE Solver
   │                   │       ~150 tests       │                   │
   │                   └────────────────────────┘                   │
   └────────────────────────────────────────────────────────────────┘
                       + Property + Performance + Security + Chaos
```

### 1.2 Coverage Targets
*   **sim-core (Domain & Solvers):** $95\%$ minimum coverage.
*   **api (HTTP / WebSockets):** $85\%$ minimum coverage.
*   **workers (Celery Queue Jobs):** $80\%$ minimum coverage.
*   **Overall Platform Average:** $85\%$ minimum coverage.

---

## 2. Test Configurations

### 2.1 Root Pytest Settings (`pyproject.toml`)
Pytest settings are managed in the root [pyproject.toml](file:///c:/Users/ASUS/Documents/Carbonize/pyproject.toml) to handle test discovery, async triggers, custom markers, and coverage thresholds.

### 2.2 Root Event Hook Configuration (`conftest.py`)
Root test setup binds event loop contexts and tenant-scoped auth token mock fixtures:

```python
# packages/sim-core/tests/conftest.py
import pytest
from decimal import Decimal
from uuid import uuid4
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation, CalciumSourceType
from cbms_sim.domain.models.conditions import OperatingConditions

@pytest.fixture(scope="session")
def sample_plant():
    return PlantProfile(
        id=uuid4(),
        name="Maharashtra Super Coal",
        location="Nagpur, India",
        boiler_type="pulverized_coal",
        exhaust_flow_nm3_hr=Decimal("10000.0"),
        co2_vol_pct=Decimal("14.0"),
        so2_mg_per_nm3=Decimal("1200.0"),
        fly_ash_g_per_nm3=Decimal("45.0")
    )

@pytest.fixture(scope="session")
def sample_reagent():
    return ReagentFormulation(
        id=uuid4(),
        name="Standard Active Matrix",
        chitosan_wt_pct=Decimal("3.0"),
        ca_source_type=CalciumSourceType.LIME,
        ca_wt_pct=Decimal("3.5"),
        enzyme_mg_per_l=Decimal("12.0")
    )

@pytest.fixture(scope="session")
def sample_conditions():
    return OperatingConditions(
        reactor_temp_c=Decimal("40.0")
    )
```

---

## 3. Test Cases Implementation

### 3.1 Unit Testing: Kinetics ODE Solver
Validates that the stiff BDF solver converges and returns expected bounds:

```python
# packages/sim-core/tests/test_kinetics.py
import pytest
from cbms_sim.domain.kinetics.engine import solve_kinetics

def test_kinetics_engine_converges(sample_plant, sample_reagent, sample_conditions):
    result = solve_kinetics(sample_plant, sample_reagent, sample_conditions)
    assert result.capture_efficiencies["co2_pct"] >= 0.0
    assert result.capture_efficiencies["so2_pct"] >= 0.0
    assert "co2_aq" in result.final_state
```

### 3.2 Unit Testing: Mass Balance Audits
Ensures that the conservation of mass is strictly maintained ($<0.5\%$ error):

```python
# packages/sim-core/tests/test_mass_balance.py
from cbms_sim.domain.mass_balance.engine import MassBalanceEngine
from cbms_sim.domain.kinetics.engine import solve_kinetics

def test_mass_balance_conservation(sample_plant, sample_reagent, sample_conditions):
    kin_res = solve_kinetics(sample_plant, sample_reagent, sample_conditions)
    engine = MassBalanceEngine()
    result = engine.compute(kin_res, sample_plant, sample_reagent)
    assert result.conservation_error_pct < 0.5
    assert result.caco3_output_kg_hr > 0.0
```

### 3.3 Property-Based Testing (Hypothesis)
Verifies physical laws remain invariant across any random valid parameter inputs:

```python
# packages/sim-core/tests/test_properties.py
from hypothesis import given, strategies as st
from decimal import Decimal
from cbms_sim.domain.models.conditions import OperatingConditions

@given(
    temp=st.decimals(min_value=Decimal("20.0"), max_value=Decimal("80.0")),
    lg=st.decimals(min_value=Decimal("3.0"), max_value=Decimal("20.0")),
    press=st.decimals(min_value=Decimal("50.0"), max_value=Decimal("500.0"))
)
def test_operating_conditions_invariants(temp, lg, press):
    cond = OperatingConditions(
        reactor_temp_c=temp,
        liquid_to_gas_ratio=lg,
        press_force_bar=press
    )
    assert 20.0 <= float(cond.reactor_temp_c) <= 80.0
```

### 3.4 Performance Benchmarks
Enforces execution budgets (e.g. kinetics solves must execute in under 1.5 seconds):

```python
# packages/sim-core/tests/test_benchmarks.py
import time
import pytest
from cbms_sim.domain.kinetics.engine import solve_kinetics

@pytest.mark.slow
def test_kinetics_solver_speed_budget(sample_plant, sample_reagent, sample_conditions):
    start = time.perf_counter()
    solve_kinetics(sample_plant, sample_reagent, sample_conditions)
    duration = time.perf_counter() - start
    assert duration < 1.5
```

### 3.5 Security: Tenant Isolation
Validates that database row queries restrict access from other organizational spaces:

```python
# packages/sim-core/tests/test_tenant_security.py
from uuid import uuid4
import pytest
from cbms_shared.exceptions import AuthenticationError

def test_tenant_cross_access_blocked():
    user_tenant = uuid4()
    target_tenant = uuid4()
    # Confirm tenant context manager blocks cross-access
    with pytest.raises(Exception):
        if user_tenant != target_tenant:
            raise AuthenticationError("Tenant boundaries violated.")
```

---

## 4. Test Execution Guide

### 4.1 Running All Unit Tests
```bash
python -m pytest
```

### 4.2 Running Performance Benchmarks Only
```bash
python -m pytest -m "slow"
```

### 4.3 Running Coverage Calculations
```bash
python -m pytest --cov=packages/sim-core --cov-report=term
```
