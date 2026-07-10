# 📂 Simulation Software File Structure: CBMS-Sim Complete Repository Blueprint

This document defines the complete repository file structure, directory boundaries, package layouts, configurations, and dependencies for the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. Monorepo Overview

CBMS-Sim is structured as a polyglot monorepo using **Poetry** for Python dependency isolation and **pnpm workspaces** for TypeScript/React packages.

```
cbms-platform/
├── packages/
│   ├── shared/                           # Shared schemas, typings, and helpers
│   ├── sim-core/                         # Pure scientific core (Python)
│   ├── api/                              # FastAPI HTTP/WebSocket gateway (Python)
│   ├── workers/                          # Celery background queue processing (Python)
│   ├── cfd/                              # snappyHexMesh & OpenFOAM CFD (C++/Python)
│   ├── web/                              # React 19 Client Dashboard (TypeScript)
│   ├── dashboards/                       # Prometheus & Grafana telemetry
│   └── infra/                            # Terraform cloud configurations
```

---

## 2. Package Blueprints

### 2.1 Backend: Sim-Core (`packages/sim-core/`)
Consists of pure mathematical and chemical physics modules without database or network dependencies:
*   `cbms_sim/domain/kinetics/`: Stiff ODE solver models using BDF methods and Numba JIT compiling.
*   `cbms_sim/domain/mass_balance/`: Stoichiometric balances verifying conservation boundaries (error $<0.5\%$).
*   `cbms_sim/domain/uq/`: Latin Hypercube Sampling (LHS) and Monte Carlo algorithms.
*   `cbms_sim/domain/sensitivity/`: Spearman Rank sensitivity analysis calculating variance shares.
*   `cbms_sim/domain/block/`: Compressive strength and density models.
*   `cbms_sim/domain/economic/`: CAPEX, OPEX, carbon credits, NPV, and payback calculators.

### 2.2 Backend: API (`packages/api/`)
FastAPI gateway directing HTTP requests, WebSocket telemetry, and security policies:
*   `cbms_api/routers/`: Tenant-isolated endpoints for plants, formulations, runs, and downloads.
*   `cbms_api/middleware/`: Handles Row-Level Security contexts and rate-limiting rules.
*   `cbms_api/db/`: SQLAlchemy schemas mapping entities (`simulation_runs`, `simulation_results`).

### 2.3 Backend: Workers (`packages/workers/`)
Celery background workers orchestrating long-running compute jobs:
*   `cbms_workers/tasks/`: Executes full LHS simulations, compiles ReportLab PDF reports, and publishes to Redis.

### 2.4 Frontend: Client Portal (`packages/web/`)
React 19 single-page application compiling via Vite:
*   `src/components/`: Modular design elements (charts, tables, parameter forms).
*   `src/hooks/`: Reactive hooks subscribing to WebSocket progress streams.

---

## 3. Configuration & CI/CD Pipelines

### 3.1 GitHub Actions Workflow (`.github/workflows/ci.yml`)
Enforces formatting (`black`), linting (`ruff`), strict type checking (`mypy`), security checks (`bandit`), and pytest suites across every pull request.

### 3.2 Workspace Devcontainer (`.devcontainer/devcontainer.json`)
Coded setup establishing unified Codespaces. Automatically installs Python 3.12, poetry, PostgreSQL client utilities, Redis cache dependencies, and the Typst CLI binary compiler.

---

## 4. Module Dependency Matrix

```
┌────────────────────────────────────────────────────────┐
│ packages/web, packages/dashboards (Layer 4)            │
└───────────┬────────────────────────────────────────────┘
            │ (REST / WebSockets)
            ▼
┌────────────────────────────────────────────────────────┐
│ packages/api, packages/workers, packages/cfd (Layer 3) │
└───────────┬────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ packages/sim-core (Layer 2)                            │
└───────────┬────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ packages/shared (Layer 1)                              │
└────────────────────────────────────────────────────────┘
```
*   **Rule:** Dependencies only point downward. The mathematical core (`sim-core`) must never import from database, routing, or worker modules.
