# 🎯 Core Features: List, Implementation, and Code Design Reference

This document provides a comprehensive technical reference for the core features of the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. Core Features Catalog

The CBMS-Sim platform implements the following 10 core features:

| Ref | Feature Name | Priority | Status | Description |
|---|---|---|---|---|
| **F-01** | Plant Profile Management | P0 (Critical) | ✅ Implemented | CRUD operations and tenant-scoped management of industrial emissions profiles. |
| **F-02** | Reagent Formulation Designer | P0 (Critical) | ✅ Implemented | Design UI and stoichiometry/cost estimators for biomineralization matrix recipes. |
| **F-03** | Simulation submission & Async Solve | P0 (Critical) | ✅ Implemented | Async Celery dispatch and orchestrator pipeline (Kinetics → UQ → Economics). |
| **F-04** | Live Progress Tracking (WS) | P0 (Critical) | ✅ Implemented | WebSockets routing progress indicators back to the React UI from Redis. |
| **F-05** | Results Dashboard with Distributions | P0 (Critical) | ✅ Implemented | Visualizer mapping point estimates, parameter distributions, and compliance alerts. |
| **F-06** | Sobol Sensitivity Analysis | P1 (High) | ✅ Implemented | Global Saltelli/Spearman-based parameter sensitivity calculation engine. |
| **F-07** | PDF Report Generation (Typst) | P1 (High) | ✅ Implemented | Feasibility report compile leveraging Typst binary and S3 storage. |
| **F-08** | CCTS Credit Claim Workflow | P1 (High) | ✅ Implemented | Indian Carbon Credit Trading Scheme eligibility verification and claim submission. |
| **F-09** | Digital Twin Real-Time Monitoring | P2 (Medium) | ✅ Implemented | Simulated real-time sensor streams and operator setpoint overrides. |
| **F-10** | Multi-Tenant Authentication & RBAC | P0 (Critical) | ✅ Implemented | JWT token scopes, tenant isolation middlewares, and role permissions. |

---

## 2. Feature Details & Integration Design

```
                     ┌──────────────────────────────┐
                     │ F-10: Multi-Tenant & RBAC    │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              F-01: Plant Profile  &  F-02: Reagent Designer             │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ (Form Submissions)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│        F-03: Async Execution  &  F-04: WS Progress Telemetry            │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ (Pipeline Completion)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ F-05: Results Dashboard  &  F-06: Sobol GSA  &  F-07: Typst PDF Reports │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│    F-08: Carbon Trading Claims (CCTS)  &  F-09: Digital Twin telemetry  │
└─────────────────────────────────────────────────────────────────────────┘
```

### F-01: Plant Profile Management
*   **Design:** Manages parameters such as `exhaust_flow_nm3_hr` and concentrations. Custom Pydantic models validate ranges (e.g. $CO_2$ must be between $0$ and $100$ vol%).
*   **Database:** Maps to `plant_profiles` table, utilizing Postgres Row-Level Security (RLS) policies targeting `org_id` parameters to guarantee tenant boundary separation.

### F-02: Reagent Formulation Designer
*   **Design:** Calculates the stoichiometric costs of materials (Lime, Steel Slag, Chitosan, Bovine/Thermostable Carbonic Anhydrase) per kg and scales them to annual operational values.
*   **Stoichiometry:** Chitosan lattice demand is estimated at $3\%$ dry solids, and bound hydration water is modeled at $15\%$ of final solid mass.

### F-03: Simulation Submission & Async Solve
*   **Design:** Submitting a simulation creates a `SimulationRun` with state `PENDING` and triggers an async task `workers.simulation.run_full_simulation` to Celery via Redis.
*   **Determinism & Reproducibility:** Serializes input configs into a SHA-256 hash. If a duplicate input hash is detected within tenant boundaries, it retrieves cached results to conserve compute cycles.

### F-04: Live Progress Tracking
*   **Design:** Workers publish progress states to Redis channels (`simulations:{run_id}:progress`). FastAPI opens a WebSocket connection, subscribing and broadcasting JSON states to the React client.

### F-05: Results Dashboard with Distributions
*   **Design:** Visualizes mean, standard deviations, and confidence intervals ($P_5, P_{95}$) for emissions capture efficiency, block compressive strength ($MPa$), and NPV cash flows.

### F-06: Sobol Sensitivity Analysis
*   **Design:** Leverages Saltelli sampling techniques to run $N \cdot (2k+2)$ model executions, computing first-order ($S_1$) and total-order ($S_T$) sensitivity indices to identify critical parameters.

### F-07: PDF Report Generation
*   **Design:** Translates simulation results into a Typst template, compiles via the local CLI compiler, and uploads the binary document to S3 with a presigned CDN download URL.

### F-08: CCTS Credit Claim Workflow
*   **Design:** Aggregates yearly $CO_2$ capture masses, verifies Indian Bureau of Energy Efficiency (BEE) compliance, and packages signed cryptographically secure claims.

### F-09: Digital Twin Real-Time Monitoring
*   **Design:** Simulates high-frequency sensor readings, tracking changes in transient pH, gas flux, temperature, and actuator statuses.

### F-10: Multi-Tenant Authentication & RBAC
*   **Design:** Encodes `user_id`, `org_id`, and `role` claims (e.g. `engineer`, `admin`, `regulator`) into a JWT. Middleware interceptors enforce tenant isolation.
