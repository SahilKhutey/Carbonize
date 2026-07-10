# ⚙️ Simulation Services: Complete Service Layer Implementation

This document provides a complete technical specification and service layer implementation reference for the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. Service Layer Architecture

Services form the application/business logic layer of the Hexagonal architecture. They are stateless, transactional, tenant-scoped orchestrators that sit between the API endpoints (controllers) and the storage/compute infrastructure.

```
┌────────────────────────────────────────────────────────────┐
│                    API CONTROLLERS                         │
│                    (REST / WebSockets)                     │
└─────────────────────────────┬──────────────────────────────┘
                              │ (Schema validated DTOs)
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                           │
│                    (ACID Boundary)                         │
├─────────────────────────────┼──────────────────────────────┤
│  Core Services:             │  Infrastructure Services:    │
│  - SimulationService        │  - TenantService             │
│  - PlantService             │  - AuditService              │
│  - ReagentService           │  - CacheService              │
│  - ReportService            │  - StorageService            │
└──────────────┬──────────────┴──────────────┬───────────────┘
               │                             │
               ▼                             ▼
┌─────────────────────────────┐┌─────────────────────────────┐
│       DOMAINS (Pure)        ││        INFRA I/O            │
│       - Solver Kernels      ││        - SQLAlchemy DB      │
│       - Mass Balances       ││        - Redis Pub/Sub      │
└─────────────────────────────┘└─────────────────────────────┘
```

---

## 2. Core Service Inventory & Catalog

The service directory structure is located under `packages/api/src/cbms_api/services/`:

| Service | Type | Domain/Role | Key Methods |
|---|---|---|---|
| `SimulationService` | Core | Simulation Orchestration | `create_simulation`, `get_results`, `cancel_simulation`, `run_baseline` |
| `OptimizationService`| Core | Bayesian parameter tuning | `submit_optimization`, `get_status` |
| `PlantService` | Core | CRUD Plant profiles | `create_plant`, `update_plant`, `delete_plant`, `list_plants` |
| `ReagentService` | Core | CRUD Matrix mixtures | `create_reagent`, `calculate_cost`, `clone_reagent` |
| `ReportService` | Core | Typst Feasibility compiling| `generate_pdf_report`, `fetch_presigned_url` |
| `AuditService` | Infra | Immutable event log | `log_event`, `list_logs` |
| `CacheService` | Infra | Redis status buffer | `get_status_cache`, `set_status_cache`, `invalidate` |

---

## 3. Core Service Implementation Specifications

### 3.1 SimulationService (`simulation_service.py`)
*   **Orchestration:** Dispatches simulation payloads to the Celery workers.
*   **Tenant Scope:** Scopes query filters targeting `org_id` values extracted from user JWT authorization headers.
*   **Caching:** Implements write-through caching on Redis (`simulation:{run_id}:status`) for high-frequency progress lookups.

### 3.2 PlantService (`plant_service.py`)
*   **Optimistic Locking:** Implements version checking on update steps:
    ```python
    if update_schema.version != plant.version:
        raise ValidationFailedError("Resource modified by another session. Please refresh.")
    ```
*   **Cascading Rules:** Verifies that no active (`PENDING` or `RUNNING`) simulation is mapped to the plant prior to soft deletion.

### 3.3 ReagentService (`reagent_service.py`)
*   **Costing Engine:** Calculates slurry costing based on exact stoichiometric component weights:
    $$\text{Slurry Cost } (₹/\text{kg}) = (W_{\text{chitosan}} \times 320) + (W_{\text{lime}} \times 8.5) + (C_{\text{enzyme}} \times 40)$$

---

## 4. Infrastructure Integration Services

### 4.1 Redis Caching & Status Dispatch
*   **Pub/Sub Event Bus:** Publishes progress values directly to Redis channels:
    ```python
    await redis_client.publish(f"simulations:{run_id}:progress", json.dumps(progress_payload))
    ```

### 4.2 S3 File Operations
*   **Storage Adapter:** Uploads compiled PDF files to S3 buckets, generating temporary CDN presigned access tokens with 15-minute expirations.
