# 🏛️ Simulation Software Architecture: Coral-Inspired Biomineralization Simulator (CBMS-Sim)

This document specifies the software architecture, design patterns, and bounded contexts for the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. Architecture Vision & Guiding Principles

### 1.1 Vision Statement
CBMS-Sim provides a scientifically defensible simulation platform that evaluates biomineralization capture networks. It supports decision-making by propagating mathematical uncertainty through all physical, chemical, and economic models.

### 1.2 Core Architectural Principles
*   **Scientific Rigor:** Every output includes propagated uncertainty bounds; no hidden defaults or point-estimate shortcuts.
*   **Modular Decoupling (Clean Architecture):** Core physics solvers (kinetics, mass balance) are strictly isolated from infrastructure boundaries (database, Web APIs, and celery queues).
*   **Bit-Exact Reproducibility:** Fixed seeds for all random number generators to ensure identical results across runs.
*   **Performance at Scale:** JIT-compiled Numba models to run 5,000-path Monte Carlo UQ campaigns in $<30\text{ seconds}$ on standard edge workers.
*   **API-First Design:** All domain service calls are exposed through OpenAPI-compliant REST endpoints.

---

## 2. Bounded Context Map (DDD)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐         │
│  │              │      │              │      │              │         │
│  │  CATALOG     │◄─────┤  SIMULATION  │─────►│  REPORTING   │         │
│  │  (Plants,    │  PL  │  (Core       │  SR  │  (PDFs,      │         │
│  │   Materials, │      │   Engine)    │      │   Dashboards)│         │
│  │   Reagents)  │      │              │      │              │         │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘         │
│         │                     │                     │                 │
│         │                     │                     │                 │
│  ┌──────▼───────┐      ┌──────▼───────┐      ┌──────▼───────┐         │
│  │              │      │              │      │              │         │
│  │  IDENTITY &  │      │  CFD/MULTI-  │      │  BILLING &   │         │
│  │  ACCESS      │      │  PHYSICS     │      │  COMPLIANCE  │         │
│  │  (Auth,      │      │  (OpenFOAM,  │      │  (CCTS,      │         │
│  │   Tenants)   │      │   Digital    │      │   Invoicing) │         │
│  │              │      │   Twin)      │      │              │         │
│  └──────────────┘      └──────────────┘      └──────────────┘         │
│                                                                       │
│  PL = Published Language   SR = Shared Kernel                        │
│  ACL = Anti-Corruption Layer at all context boundaries              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 Bounded Contexts
1.  **Catalog Bounded Context:** Manages plant profiles, raw coal compositions, lime purity files, and local utility cost indexes.
2.  **Simulation Bounded Context:** Core mathematical solver orchestrating kinetics, mass balance, Wiener saturation, and economic NPV/IRR models.
3.  **CFD Bounded Context:** Prepares meshes and runs OpenFOAM solver slipstream cases.
4.  **Reporting Bounded Context:** Assembles and cures PDF validation certificates.
5.  **Identity Context:** Manages tenant scopes and RBAC.

---

## 3. Container & Component Models (C4 Level 2/3)

### 3.1 Container Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  React 19 SPA Client                                        │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │   Input Calibration   │   │   Simulation Workbench    │  │
│  └───────────────────────┘   └───────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / WebSockets
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI API Gateway                                        │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │   REST Routes         │   │   WS Event Broadcaster    │  │
│  └───────────────────────┘   └───────────────────────────┘  │
└─────┬───────────────────────────────────────────────────┬───┘
      │ Enqueues Async Task                               │ Database Access
      ▼                                                   ▼
┌──────────────────────────┐                   ┌──────────────────────────┐
│  Redis Task Broker       │                   │  RDS PostgreSQL DB       │
│  (Celery Queue)          │                   │  (Timescale Extension)   │
└──────────┬───────────────┘                   └──────────────────────────┘
           │ Dispatches Job
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Celery Compute Workers                                     │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │  UQ/Kinetics Solver   │   │   Typst PDF Compiler      │  │
│  └───────────────────────┘   └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Dependencies (Hexagonal Pattern)
The core codebase is structured around ports and adapters:
*   **Domain Core:** Contains pure python mathematical models, entities, and value objects (`PlantProfile`, `SimulationRun`, `KineticsSolver`). Contains zero I/O imports (no database connections, HTTP calls, or file system writes).
*   **Application Ports:** Interface definitions (`SimulationRepositoryPort`, `PDFCompilerPort`).
*   **Infrastructure Adapters:** Database adapters (`SQLAlchemyRepository`), task runners (`CeleryAdapter`), and S3 storage connectors.

---

## 4. Database Architecture & Schema Design

### 4.1 Data Stores
1.  **PostgreSQL (Transactional):** Stores plant parameters, simulation requests, user records, and output metrics.
2.  **TimescaleDB Extension:** Ingests high-frequency time-series logs (flue gas temperatures, stack SO₂ levels) from field sensors.
3.  **Redis:** Coordinates Celery worker locks and caches dashboard queries.

### 4.2 Core Tables Schema (DDL Outline)
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE plant_profiles (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    exhaust_flow_rate DOUBLE PRECISION NOT NULL,
    baseline_temperature DOUBLE PRECISION NOT NULL,
    co2_concentration DOUBLE PRECISION NOT NULL,
    so2_concentration DOUBLE PRECISION NOT NULL,
    fly_ash_load DOUBLE PRECISION NOT NULL
);

CREATE TABLE simulation_runs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    plant_profile_id UUID REFERENCES plant_profiles(id),
    status VARCHAR(50) NOT NULL,
    press_force_bar DOUBLE PRECISION NOT NULL,
    enzyme_concentration_mg_l DOUBLE PRECISION NOT NULL,
    chitosan_wt_pct DOUBLE PRECISION NOT NULL
);

CREATE TABLE simulation_results (
    id UUID PRIMARY KEY,
    simulation_run_id UUID REFERENCES simulation_runs(id) UNIQUE,
    co2_capture_efficiency_pct DOUBLE PRECISION NOT NULL,
    so2_capture_efficiency_pct DOUBLE PRECISION NOT NULL,
    predicted_block_strength_mpa DOUBLE PRECISION NOT NULL,
    block_grade VARCHAR(100) NOT NULL,
    capex_total_inr DOUBLE PRECISION NOT NULL,
    annual_opex_inr DOUBLE PRECISION NOT NULL,
    simple_payback_months DOUBLE PRECISION NOT NULL,
    npv_10yr_inr DOUBLE PRECISION NOT NULL,
    irr_pct DOUBLE PRECISION NOT NULL
);
```

---

## 5. Async Compute & Job Orchestration

```
User Click "Solve" ──> API Gateway ──> Enqueue Run ID ──> Celery Worker
                                                            │
                                                            ├──> Solve ODE (BDF)
                                                            ├──> Compute Balances
                                                            ├──> Run 5,000 UQ runs
                                                            ▼
                                                        Write to Database
                                                            │
                                                            ▼
                                                     Broadcaster Event
```
Celery workers poll the Redis broker. Heavy tasks are routed to a dedicated `compute` queue, while light operations (PDF generation, email notification) run on the `default` queue.

---

## 6. Uncertainty Quantification (UQ) Subsystem

The UQ engine uses **Latin Hypercube Sampling (LHS)** to distribute model uncertainty:
1.  **Parameter Spanning:** Configures Gaussian probability distributions for the chemical kinetics coefficients (e.g., $k_{\text{cat}}$ and $K_{\text{M}}$).
2.  **LHS Sampling:** Draws 5,000 parameter combinations to execute the solver.
3.  **Sobol Indices:** Calculates first-order ($S_i$) and total-effect ($S_{Ti}$) Sobol indices to evaluate variance contribution:
    \[
    S_i = \frac{V_i}{V(Y)} = \frac{V_{X_i}(E_{X_{\sim i}}(Y \mid X_i))}{V(Y)}
    \]
4.  **Critical Experiments List:** Auto-ranks variables with $S_i > 0.10$ to guide laboratory testing focus.

---

## 7. Observability & Monitoring

*   **Metric Logs:** Promtail + Loki aggregating application exception logs.
*   **System Telemetry:** Prometheus tracking API request latency, queue lengths, and active compute workers.
*   **Visualization:** Grafana dashboards displaying operational KPIs.

---

## 8. Package & Directory Structure

```
biomimetic_sim/
│
├── api/                               # FastAPI routing layer
│   ├── routes/                        # Domain REST endpoints
│   ├── dependencies.py                # Database and safety injectables
│   └── main.py                        # Server launch file
│
├── core/                              # Pure mathematical solvers
│   ├── config.py                      # Constants & parameters
│   ├── kinetics.py                    # Stiff ODE kinetics solver
│   ├── mass_balance.py                # Conservation equations
│   ├── block_strength.py              # Strength & grade classification
│   └── economic_engine.py             # OPEX/CAPEX, NPV/IRR sizer
│
├── database/                          # Persistence layer
│   ├── connection.py                  # Async connection pool
│   └── models.py                      # ORM entity tables
│
├── ml/                                # Layer 9 ML and Optimizers
│   ├── surrogate_model.py             # GP regression model
│   └── bayesian_optimizer.py          # Optuna optimizer
│
├── workers/                           # Celery queue worker engines
│   ├── celery_app.py                  # Task initialization
│   ├── tasks.py                       # Compute tasks definitions
│   └── report_generator.py            # PDF compilation scripts
│
└── tests/                             # Verification tests suites
```
