# 🔄 Simulation Software Pipeline: CBMS-Sim End-to-End Data & Control Flow

This document defines the mathematical, physical, and economic data pipelines, transformation stages, schema contracts, and implementation blueprints for the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. Pipeline Architecture Overview

### 1.1 Pipeline Definition
A pipeline is a directed acyclic graph (DAG) of data transformations. Each stage consumes typed inputs from the preceding stage, runs calculations, and yields validated outputs for the next stage.
*   **Stateless Execution:** Each pipeline pass is deterministic and reproducible (given identical inputs and RNG seed).
*   **Typed Boundaries:** Bound contracts at each stage boundary are validated using Pydantic schemas or Python dataclasses.
*   **Decoupled Compute:** Computation-heavy stages (Monte Carlo, Sobol sensitivity) are isolated to run on dedicated multiprocessing pools.

### 1.2 Pipeline Tier Model
```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: REQUEST PIPELINE (Synchronous, <500ms)             │
│  - Authentication check                                     │
│  - Validation (Pydantic v2 schemas)                         │
│  - Enqueues background Celery job                           │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: ORCHESTRATION PIPELINE (Asynchronous, Celery)      │
│  - Manages task state: PENDING -> RUNNING -> COMPLETED      │
│  - Emits real-time progress to Redis pub/sub channel        │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: COMPUTE PIPELINE (CPU-Bound, Worker Processes)    │
│  - Runs BDF ODE kinetics solver                             │
│  - Evaluates mass balances & conservation constraints        │
│  - Executes Latin Hypercube UQ & Spearman correlation loops  │
├─────────────────────────────────────────────────────────────┤
│  TIER 4: PERSISTENCE PIPELINE (I/O-Bound, <2s)              │
│  - Stores simulation run & results                          │
│  - Invalidates cache tags                                   │
├─────────────────────────────────────────────────────────────┤
│  TIER 5: DELIVERY PIPELINE (Asynchronous, Typst render)     │
│  - Assembles result parameters into PDF reports             │
│  - Uploads PDF output files to AWS S3                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline Execution Stages

```
   [Stage 0: Input Validation]
               │
               ▼
   [Stage 1: Parameter Binding]
               │
               ▼
   [Stage 2: Kinetics Solver] (Stiff ODE solver)
               │
               ▼
   [Stage 3: Mass Balance Solver] (Stoichiometric checks)
               │
               ▼
   [Stage 4: Block Property Predictor] (Empirical model)
               │
               ▼
   [Stage 5: Uncertainty Quantification] (LHS sampling)
               │
               ▼
   [Stage 6: Global Sensitivity] (Spearman Rank metrics)
               │
               ▼
   [Stage 7: Economic / Payback Analysis] (NPV/IRR engine)
               │
               ▼
   [Stage 8: Result Persistence] (PostgreSQL / TimescaleDB)
               │
               ▼
   [Stage 9: PDF Compilation & Publish] (Typst compile to S3)
```

### 2.1 Stage 0: Input Ingestion & Validation
*   **Action:** Parse incoming JSON payload using `SimulationRequestSchema`. Verify authorization context via header token.
*   **Failure Check:** Refuse values outside allowable physics ranges (e.g. flow rates outside $[100, 500000]\text{ Nm}^3\text{/hr}$).

### 2.2 Stage 1: Parameter Resolution & Binding
*   **Action:** Merges user parameters, defaults, and physical coefficients into an immutable database-safe set.
*   **Output:** Flat key-value parameters tagged with standard deviations and citation DOIs for downstream traceability.

### 2.3 Stage 2: Kinetics Solve (Deterministic)
*   **Action:** Integrates the coupled reaction kinetics ODE system (enzymatic $\text{CO}_2$ hydration, deacetylation, and mineral precipitation) using a Backward Differentiation Formula (BDF) stiff integrator.
*   **Failure Check:** Returns an error if the solver diverges or fails to converge within the residence time bounds.

### 2.4 Stage 3: Mass Balance & Stoichiometry
*   **Action:** Converts volumetric concentrations to mass flows ($\text{kg/hr}$). Checks conservation equations.
*   **Verification:** Rejects the run if total mass conservation error is $>0.5\%$.

### 2.5 Stage 4: Block Property Prediction
*   **Action:** Calculates block compressive strength ($\text{MPa}$) and density based on calcite yield, ash ratios, compaction force, and curing hours.
*   **Classification:** Maps properties to standard Indian Standard (IS) block grades (e.g. M25, M20, substandard).

### 5.6 Stage 5: Uncertainty Quantification (Monte Carlo)
*   **Action:** Draws 5,000 parameter combinations using Latin Hypercube Sampling (LHS) across parameter variance ranges.
*   **Computation:** Executes parallel forward solver passes across a CPU multiprocessing pool to find standard deviations and confidence intervals.

### 2.7 Stage 6: Global Sensitivity (Spearman Rank)
*   **Action:** Evaluates Spearman Rank correlation metrics between LHS input distributions and the $\text{CO}_2$ capture efficiency outputs.
*   **Sensitivity Index:** Returns normalized sensitivity shares. Generates the critical experiments ranking list to prioritize laboratory validation.

### 2.8 Stage 7: Economic & Compliance Modeling
*   **Action:** Runs financial modeling equations (CAPEX, OPEX, annual carbon credit revenues under CCTS, 10-year NPV, IRR, and simple payback).
*   **CPCB Check:** Compares outlet gas concentrations against CPCB air pollution limits ($\text{SO}_2 < 200\text{ mg/Nm}^3$).

### 2.9 Stage 8: Result Composition & Persistence
*   **Action:** Combines calculations and sensitivity matrices into a single transaction. Saves records to `simulation_results`.

### 2.10 Stage 9: Report Generation & Publication
*   **Action:** Compiles the PDF report using the Typst binary compiler and uploads it to AWS S3.

---

## 3. Data Flow Contracts

```
[SimulationRequestSchema] ──► [BoundParameterSet] ──► [KineticsResult] ──► [MassBalanceResult] ──► [SimulationResult]
```

### 3.1 Schema Declarations (Python Dataclass Contracts)
```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class BoundParameterSet:
    parameters: Dict[str, float]
    provenance_version: str
    input_hash: str

@dataclass(frozen=True)
class KineticsResult:
    co2_capture_efficiency_pct: float
    so2_capture_efficiency_pct: float
    metal_chelated_pct: float
    equilibrium_ph: float

@dataclass(frozen=True)
class MassBalanceResult:
    caco3_output_kg_hr: float
    gypsum_output_kg_hr: float
    fly_ash_captured_kg_hr: float
    chitosan_lattice_kg_hr: float
    conservation_error_pct: float
    cpcb_compliant: bool
```

---

## 4. Pipeline Performance Engineering

*   **Numba JIT Compilation:** RHS kinetics math routines are pre-compiled to machine code via LLVM. Warm calls run in $<1\text{ ms}$.
*   **Chunked Multiprocessing:** Monte Carlo samples are split into chunks and processed in parallel across worker CPU pools (e.g. 50 tasks $\times$ 100 iterations), preventing process start overhead.
*   **Memory Footprint:** Keeps memory usage $<120\text{ MB}$ per execution block by utilizing compact NumPy float64 array buffers and pre-allocating output vectors.
