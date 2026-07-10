# ⚙️ Simulation Software Workflow: CBMS-Sim End-to-End Pipeline

This document defines the operational workflow, actor journey maps, task state machines, and coordination pipelines for the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. Workflow Architecture Overview

### 1.1 The Three-Plane Model
*   **Plane 1: User Interaction Plane (Synchronous, HTTP/WS):** Deals with incoming REST API requests, WebSocket sessions, and user triggers. Requires response latencies $<5\text{ seconds}$.
*   **Plane 2: Orchestration Plane (Asynchronous, Event-Driven):** Manages simulation state machines, celery job schedules, and pub/sub event routing. Runs in minutes.
*   **Plane 3: Compute Plane (CPU/IO-Bound, Workers):** Performs deterministic kinetics solving, Monte Carlo sampling, and block strength calculations. Runs in seconds to hours (for CFD).
*   **Cross-Plane: Data Plane (Persistent Storage):** Houses PostgreSQL database records, TimescaleDB time-series logs, and S3 artifact files.

---

## 2. Primary Workflow: Standard Simulation Run

```
User Click "Run" ──> [PLANE 1: FastAPI] ──> Write PENDING ──> [PLANE 2: Redis Broker]
                                                                      │
                                                                      ▼
  [PLANE 1: WS Update] <── Write RUNNING <── Pick up Job ◄── [PLANE 3: Celery Worker]
           │                                                          │
           ├──> Solve Kinetics (Numba) ───────────────────────────────┤
           ├──> Compute Mass Balances ────────────────────────────────┤
           ├──> Run Monte Carlo (5,000 runs) ─────────────────────────┤
           ▼                                                          ▼
  [PLANE 1: WS Update] <── Write COMPLETED <── Save Results ◄─────────┘
```

### 2.1 Workflow Steps
1.  **POST `/simulations`:** User submits a simulation request carrying target plant and reagent profiles.
2.  **Validate & Authenticate:** FastAPI processes input shapes (Pydantic validation) and extracts JWT parameters.
3.  **Insert PENDING:** A new row is written to `simulation_runs` with `PENDING` status.
4.  **Enqueue Worker Job:** API gateway publishes a task payload to the Redis queue.
5.  **202 Accepted Response:** Instantly returned to the client, providing a tracking UUID.
6.  **Worker Pick Up:** A free Celery worker de-queues the job and updates status to `RUNNING`.
7.  **Core Forward Solver:** Executed sequentially:
    *   *Kinetics:* Solves the stiff BDF ODE system for gas-liquid carbonate kinetics.
    *   *Mass Balance:* Evaluates stoichiometry and raw conservation indices.
    *   *Wiener Process:* Simulates mesh loading and saturation First Passage Time (FPT).
    *   *Block Strength:* Predicts compressive properties and IS grade.
    *   *Financials:* Calculates NPV, IRR, and OPEX metrics.
8.  **Monte Carlo UQ:** Draws 5,000 LHS samples using Latin Hypercube grids to calculate Spearman Rank sensitivity metrics.
9.  **Write Results:** Saves statistical summaries and outputs to `simulation_results` and marks status as `COMPLETED`.
10. **Report Compilation:** Triggers the Typst renderer to write a PDF file and save it in Amazon S3.

---

## 3. Actor Journey Maps

### 3.1 Plant Engineer: "Will this work at my plant?"
1.  **Profile Entry:** Input local stack emissions (exhaust flow rate, baseline temperatures, and $\text{CO}_2$ concentration).
2.  **Reagent Definition:** Select enzyme dosage (mg/L), chitosan matrix levels ($\text{wt}\%$), and compaction force (bar).
3.  **Run Trigger:** Submits simulation. Watches progress bar update via live WebSocket events.
4.  **Result Inspection:** Compares predicted $\text{CO}_2$/$\text{SO}_2$ capture efficiencies and block grades against standard structural specifications.

### 3.2 CFO: "What is the economic payback?"
1.  **Drill Down:** Evaluates financial projections (CAPEX, OPEX, NPV, IRR, and payback periods).
2.  **GST & Credits:** Audits GST allocations and carbon offset credits under local BEE guidelines.
3.  **Export Data:** Downloads Excel financial models.

---

## 4. State Machines

### 4.1 Simulation Run States
```
 (Start) ──► PENDING ──► RUNNING ──► COMPLETED (Success)
                           │
                           ├──► FAILED (Exception log written)
                           │
                           └──► TIMEOUT (Exceeded max worker limit)
```

### 4.2 Report Generation States
```
 REQUESTED ──► QUEUED ──► RENDERING (Typst compile) ──► UPLOADING (S3) ──► AVAILABLE
```

---

## 5. CFD Coupling Workflow

```
Solve 1D Core Solver ──> Map boundary conditions ──> Prepare Mesh ──> Run OpenFOAM
                                                                           │
                                                                           ▼
   Update effective kLa <── Extract fields <── Complete Solve ◄────────────┘
```
1.  **1D Initialization:** Run fast baseline solver to define reactor inlet boundaries.
2.  **OpenFOAM Case Prep:** Auto-generates structural mesh grids around reaction towers.
3.  **Solver Execution:** Runs parallel bubble column solvers (Euler-Euler multiphase).
4.  **Field Extraction:** Extracts gas-liquid volume fractions and velocity matrices to refine the 1D solver's mass transfer coefficients ($k_L a$).

---

## 6. Digital Twin Real-Time Workflow

```
Continuous Sensor feed (Modbus/MQTT) ──> Ingest (TimescaleDB) ──> Run GP Surrogate
                                                                        │
                                                                        ▼
           Update control targets <── Alert operator <── Evaluate Delta ┘
```
1.  **Telemetry Ingest:** Continuous sensor feed (pressures, temperatures, outlet $\text{CO}_2$) sent to TimescaleDB via Modbus/MQTT.
2.  **Surrogate Evaluation:** Runs the Gaussian Process surrogate model every 30 seconds.
3.  **Alerting:** Raises alarms if physical outputs diverge from theoretical predictions by $>15\%$, indicating potential enzyme deactivation or line fouling.

---

## 7. Report Generation Workflow

*   **Document Assembly:** Extracts simulation results, inputs, and UQ sensitivity rankings into a structured JSON payload.
*   **Typst Compiler:** Invokes the Typst CLI binary inside workers to compile high-quality PDF reports in $<2\text{ seconds}$.
*   **Object Storage:** Uploads PDFs to AWS S3 using presigned URLs with a 7-day expiration policy.

---

## 8. Compliance & CCTS Workflow

*   **Audit Logging:** Saves transaction logs (timestamps, user ID, raw sensor input averages) in an immutable PostgreSQL database schema.
*   **Emissions Verification:** Maps verified $\text{CO}_2$ capture tons to BEE-compliant carbon credits:
    \[
    \text{Credits}_{\text{BEE}} = \text{Tons}_{\text{CO2 Captured}} \times \text{Purity Factor} \times (1.0 - \text{Parasitic Load Penalty})
    \]
*   **Registry Publish:** Interfaces via REST APIs with regulatory portals to submit monthly emissions logs.

---

## 9. Performance Budgets

*   **API Route Latency (p95):** $<200\text{ ms}$ for baseline configurations.
*   **Standard Simulation Time:** $<45\text{ seconds}$ on standard dual-core worker nodes.
*   **PDF Report Render:** $<5\text{ seconds}$ from database fetch to S3 write.
*   **Maximum Queue Wait Time:** $<10\text{ seconds}$ under standard load.

---

## 10. Workflow Implementation Pseudocode

```python
# Conceptual Celery worker workflow orchestration
from celery import shared_task
from database.connection import async_session_maker
from core.kinetics import solve_reactor_kinetics
from core.mass_balance import compute_mass_balance
from core.uncertainty_engine import run_uncertainty_analysis
from core.block_strength import predict_compressive_strength
from core.economic_engine import run_financial_analysis

@shared_task(name="workers.tasks.run_complete_pipeline")
def run_complete_pipeline(run_id_str: str, temp_c: float = 40.0):
    """
    Orchestrates the entire end-to-end simulation workflow.
    """
    # 1. Initialize DB Session and load models
    # 2. Mark state as RUNNING
    # 3. Step 1: Run kinetics ODE system
    # 4. Step 2: Run mass balance and chemical conservation checks
    # 5. Step 3: Run Monte Carlo UQ to compute standard deviations and sensitivity
    # 6. Step 4: Predict block compressive strength and IS grade classification
    # 7. Step 5: Execute financial projection calculations
    # 8. Step 6: Generate Typst PDF, write to S3, and update DB state to COMPLETED
    pass
```
