# 📋 Modules and Functions Registry: CBMS-Sim Implementation Reference

This document provides a comprehensive technical specification of every module, class, and critical function in the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. Monorepo Package Topology

```
cbms-platform/
├── packages/
│   ├── shared/                           # Layer 0: Logging, constants, semantic types, exceptions
│   ├── sim-core/                         # Layer 1: Kinetics solver, mass balance, UQ engines, economics
│   ├── api/                              # Layer 2: FastAPI routes, middlewares, RLS database schema
│   ├── workers/                          # Layer 3: Celery task workers, event buses
│   └── web/                              # Layer 4: React web dashboards, chart visualizers
```

---

## 2. Package 1: Shared (`packages/shared/`)

Provides common configurations, exception classes, and semantic type aliases used across the platform.

### 2.1 Module `cbms_shared.exceptions`
*   `CBMSError(message, code, **context)`: Base class with standard serialization capabilities via `to_dict()`.
*   `ScientificError(CBMSError)`: Base for chemical simulation failures.
*   `NumericalDivergenceError(ScientificError)`: Raised when the BDF kinetics integration fails to converge.
*   `InvalidParameterError(ScientificError)`: Raised when input parameters fall outside chemical limits.
*   `UQConvergenceError(ScientificError)`: Raised if Latin Hypercube or Sobol indices fail convergence limits.

### 2.2 Module `cbms_shared.types`
*   `PlantId`: Multi-tenant tenant identifier (`NewType("PlantId", UUID)`).
*   `CaptureEfficiency`: Value restricted between `0.0` and `100.0` percent.
*   `Concentration`: Volumetric chemical concentration in $\text{mol/m}^3$.

### 2.3 Module `cbms_shared.constants`
*   `R_GAS`: Universal gas constant ($8.314\text{ J/(mol}\cdot\text{K)}$).
*   `MOLAR_MASSES`: Dictionary of critical species (e.g., $\text{CO}_2$: $44.01$, $\text{Ca(OH)}_2$: $74.10$).
*   `CPCB_SO2_LIMIT_MG_PER_NM3`: India CPCB regulatory limit ($200.0\text{ mg/Nm}^3$).

### 2.4 Module `cbms_shared.logging`
*   `configure_logging(level, json_output)`: Configures structlog with JSON rendering for Docker outputs.
*   `get_logger(name)`: Retrieves namespace-bound structured loggers.

---

## 3. Package 2: Sim-Core (`packages/sim-core/`)

Scientific computational package. Free of network and databases.

### 3.1 Module `cbms_sim.domain.models`
*   `PlantProfile`: Exposes flue gas properties (`exhaust_flow_nm3_hr`, `co2_vol_pct`, `so2_mg_per_nm3`).
*   `ReagentFormulation`: Details capturing matrix recipes (`chitosan_wt_pct`, `enzyme_mg_per_l`).
*   `OperatingConditions`: Defines process parameters (`reactor_temp_c`, `pH_initial`, `liquid_to_gas_ratio`).

### 3.2 Module `cbms_sim.domain.kinetics`
*   `KineticsEngine.solve(plant, reagent, conditions)`:
    *   **Work:** Formulates state vectors and integrates the stiff ODE system.
    *   **Implementation:** Calls SciPy's `solve_ivp` utilizing the stiff `"BDF"` method, calling JIT compiled kernels.
*   `reaction_rhs_numba(t, y, ...)`:
    *   **Work:** Solves 9 species differential rates including CA deactivation, calcite growth, gypsum precipitation, metal chelation, and particulate trapping.
    *   **Implementation:** Decorated with `@njit(cache=True)` for ~50x speedups.

### 3.3 Module `cbms_sim.domain.mass_balance`
*   `MassBalanceEngine.compute(kinetics, plant, reagent)`:
    *   **Work:** Performs conservation mass audits across solid, liquid, and gas streams.
    *   **Implementation:** Resolves calcium demand, mineral yields ($\text{CaCO}_3$, $\text{CaSO}_4$), and verifies that atomic error remains $<0.5\%$.

### 3.4 Module `cbms_sim.domain.uq`
*   `MonteCarloEngine.run(forward_fn, parameter_specs)`:
    *   **Work:** Resolves parametric uncertainties under varying operating scenarios.
    *   **Implementation:** Generates Latin Hypercube samples (`scipy.stats.qmc.LatinHypercube`), evaluates runs in parallel, and computes $P_5, P_{50}, P_{95}$ confidence intervals.

---

## 4. Package 3: API (`packages/api/`)

FastAPI gateway handling HTTP requests and WebSocket telemetry streams.

### 4.1 Module `cbms_api.routers.simulations`
*   `submit_simulation`: Enqueues an async simulation run task to Celery. Returns a `202 Accepted` status.
*   `stream_progress`: Establish WebSockets tracking live simulation steps from Redis.

### 4.2 Module `cbms_api.db.models`
*   SQLAlchemy ORM schemas mapping multi-tenant boundaries (`Organization`, `User`, `SimulationRun`, `SimulationResult`). Uses Postgres RLS (Row-Level Security) patterns.

---

## 5. Package 4: Workers (`packages/workers/`)

Celery-driven asynchronous job executor.

### 5.1 Module `cbms_workers.tasks`
*   `run_full_simulation(run_id)`: Orchestrates the orchestrator pipeline, extracts results, uploads reports, and publishes progress logs back to the Redis broker.
