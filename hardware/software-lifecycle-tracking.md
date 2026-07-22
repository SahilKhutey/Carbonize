# Software Specification: Materials & Reactor Lifecycle Tracking

**Companion to:** [`hardware/materials-spec.md`](file:///c:/Users/ASUS/Documents/Carbonize/hardware/materials-spec.md)  
**Owner:** Platform Engineering / Operator Experience  
**Status:** 🟡 Specification Complete — Implementation Pending Pilot Hardware  
**Last updated:** 2026-07-20

---

## 1. Overview

`materials-spec.md` documents the physical materials, component lifetimes, and consumable replacement schedules for the reactor. This software specification covers:

1. **Consumable lifecycle tracking** — enzyme beads, mesh cartridges, O-rings, gaskets
2. **Reagent inventory management** — Ca(OH)₂ slurry, chitosan solution, calibration gases
3. **Component health estimation** — predictive wear models for impeller, mesh, seals
4. **Maintenance workflow** — work orders, technician assignment, completion sign-off
5. **Cost tracking** — per-component and aggregate OPEX reporting

---

## 2. Data Model

### 2.1 Component Registry

```sql
-- Alembic migration: 0025_add_component_lifecycle_tables.py

CREATE TABLE reactor_components (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id        UUID NOT NULL REFERENCES plant_profiles(id),
    component_key   TEXT NOT NULL,       -- e.g. 'enzyme_beads', 'pp_mesh_01'
    component_type  TEXT NOT NULL,       -- 'consumable' | 'semi-permanent' | 'permanent'
    material        TEXT NOT NULL,       -- e.g. 'glutaraldehyde_chitosan'
    installed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expected_life_days INT,              -- from materials-spec.md
    last_replaced_at TIMESTAMPTZ,
    replacement_cost_inr INT,
    notes           TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (plant_id, component_key)
);

CREATE TABLE component_lifecycle_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id    UUID NOT NULL REFERENCES reactor_components(id),
    event_type      TEXT NOT NULL,       -- 'installed' | 'inspected' | 'replaced' | 'failed'
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    technician_id   UUID REFERENCES users(id),
    notes           TEXT,
    cost_inr        INT,
    sensor_readings JSONB               -- snapshot of key readings at event time
);
```

### 2.2 Consumable Schedules (from materials-spec.md)

```python
# packages/api/src/cbms_api/services/lifecycle.py

COMPONENT_SCHEDULES = {
    "enzyme_beads": {
        "type":               "consumable",
        "replacement_days":   30,         # monthly replenishment
        "cost_inr_per_cycle": 500,        # ₹500/month
        "material":           "glutaraldehyde_cross_linked_chitosan",
        "reuse_cycles":       20,         # 20-50 per spec
        "warning_days_before": 7,         # alert 7 days before due
    },
    "pp_mesh_cartridge": {
        "type":               "consumable",
        "replacement_days":   60,         # 6 pcs/year → every ~60 days
        "cost_inr_per_cycle": 700,        # ₹4200 / 6 = ₹700 each
        "material":           "polypropylene_200um",
        "warning_days_before": 10,
    },
    "epdm_oring_set": {
        "type":               "semi-permanent",
        "replacement_days":   180,        # 6-month inspection
        "cost_inr_per_cycle": 600,        # ₹200 × 3 per set
        "material":           "EPDM",
        "warning_days_before": 14,
    },
    "ptfe_gasket_set": {
        "type":               "semi-permanent",
        "replacement_days":   365,
        "cost_inr_per_cycle": 1800,
        "material":           "virgin_PTFE",
        "warning_days_before": 21,
    },
    "impeller_pp_coating": {
        "type":               "semi-permanent",
        "replacement_days":   365,        # annual inspection for coating wear
        "cost_inr_per_cycle": 8500,
        "material":           "PP_coated_316L_SS",
        "warning_days_before": 30,
    },
    "zero_gas_n2": {
        "type":               "consumable",
        "replacement_days":   30,         # monthly cylinder
        "cost_inr_per_cycle": 3000,
        "material":           "N2_99.999",
        "warning_days_before": 7,
    },
    "so2_span_gas": {
        "type":               "consumable",
        "replacement_days":   90,         # quarterly
        "cost_inr_per_cycle": 4000,       # ₹8K / 2 gases
        "material":           "SO2_50ppm_in_N2",
        "warning_days_before": 14,
    },
    "nox_span_gas": {
        "type":               "consumable",
        "replacement_days":   90,
        "cost_inr_per_cycle": 4000,
        "material":           "NOx_50ppm_in_N2",
        "warning_days_before": 14,
    },
}
```

---

## 3. Reagent Inventory

### 3.1 Inventory Table

```sql
CREATE TABLE reagent_inventory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id        UUID NOT NULL REFERENCES plant_profiles(id),
    reagent_key     TEXT NOT NULL,       -- 'ca_oh2_slurry' | 'chitosan_solution'
    unit            TEXT NOT NULL,       -- 'kg' | 'L' | 'cylinder'
    quantity        DOUBLE PRECISION NOT NULL DEFAULT 0,
    reorder_level   DOUBLE PRECISION NOT NULL,
    reorder_qty     DOUBLE PRECISION NOT NULL,
    cost_per_unit_inr DOUBLE PRECISION,
    supplier        TEXT,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE reagent_consumption_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id    UUID NOT NULL,
    reagent_key TEXT NOT NULL,
    consumed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    quantity    DOUBLE PRECISION NOT NULL,     -- computed from flow meter
    source      TEXT NOT NULL DEFAULT 'auto',  -- 'auto' | 'manual'
    run_id      UUID REFERENCES simulation_runs(id)
);
```

### 3.2 Auto-Consumption from Flow Meters

The simulation worker reads reagent flow data from `FLOW-REG-01` (Ca(OH)₂ Coriolis) and `FLOW-CHI-01` (chitosan dosing pump) to automatically decrement inventory:

```python
async def update_reagent_inventory(plant_id: UUID, readings: dict, db: AsyncSession):
    """
    Called every 60 seconds by the telemetry consumer.
    Calculates consumption from flow meter readings × elapsed time.
    Decrements reagent_inventory.quantity.
    Creates consumption_log entries.
    Raises low-stock alert if quantity < reorder_level.
    """
    ca_flow_l_min = readings.get("FLOW-REG-01", 0.0)   # L/min
    chi_flow_l_min = readings.get("FLOW-CHI-01", 0.0)  # L/min
    elapsed_min = 1.0

    await _consume(plant_id, "ca_oh2_slurry", ca_flow_l_min * elapsed_min, db)
    await _consume(plant_id, "chitosan_solution", chi_flow_l_min * elapsed_min, db)
```

---

## 4. Predictive Wear Models

### 4.1 Enzyme Bead Degradation Model

Based on the materials-spec reuse cycle data (20–50 cycles, operating at pH 8–10, 40–50°C):

```python
def enzyme_activity_pct(
    days_since_replacement: float,
    temp_c: float = 43.0,
    ph: float = 9.0,
) -> float:
    """
    First-order decay model:
      A(t) = 100 × exp(−k_deg × t)

    k_deg is Arrhenius-sensitive:
      k_deg = k_ref × exp(Ea/R × (1/T_ref − 1/T))

    Calibrated to: 50% activity retained at 30 days (nominal conditions).
    pH correction: activity drops 5% per 0.5 units above pH 10.
    """
    k_ref = 0.0231  # day⁻¹ → half-life ~30 days at 43°C, pH 9
    T_k   = temp_c + 273.15
    T_ref = 316.15  # 43°C reference
    Ea_R  = 5500.0  # Ea/R in Kelvin (calibrate from lab data)
    k_deg = k_ref * math.exp(Ea_R * (1/T_ref - 1/T_k))

    ph_penalty = max(0.0, (ph - 10.0) * 0.1) if ph > 10.0 else 0.0
    activity = 100.0 * math.exp(-k_deg * days_since_replacement) - ph_penalty * 100
    return max(0.0, min(100.0, activity))
```

**Replacement trigger:** when `enzyme_activity_pct < 50` → work order auto-created.

### 4.2 Mesh Fouling Index

```python
def mesh_fouling_index(
    dp_across_mesh_mbar: float,
    dp_clean_mbar: float = 15.0,   # baseline ΔP for clean mesh
    dp_replace_mbar: float = 45.0, # ΔP at which replacement is needed
) -> float:
    """Returns 0 (clean) → 100 (replace needed)."""
    if dp_across_mesh_mbar <= dp_clean_mbar:
        return 0.0
    return min(100.0, (dp_across_mesh_mbar - dp_clean_mbar)
               / (dp_replace_mbar - dp_clean_mbar) * 100.0)
```

**Replacement trigger:** `mesh_fouling_index > 75` → work order auto-created.

### 4.3 Coating Wear Proxy (Impeller)

Since we cannot directly measure PP coating thickness, we use ORP trend as a proxy:

- **Healthy coating:** ORP steady, no rapid fluctuations
- **Coating degrading:** ORP variance increases (SS substrate beginning to be exposed)

```python
def impeller_coating_health_score(orp_readings_last_24h: list[float]) -> float:
    """
    Returns 0 (urgent inspect) → 100 (healthy).
    Based on ORP rolling standard deviation.
    Threshold: std > 25 mV → score drops below 60 → inspection alarm.
    """
    if not orp_readings_last_24h:
        return 100.0
    std = statistics.stdev(orp_readings_last_24h)
    score = max(0.0, 100.0 - (std / 0.25))
    return score
```

---

## 5. Work Order System

```sql
CREATE TABLE maintenance_work_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id        UUID NOT NULL REFERENCES plant_profiles(id),
    component_id    UUID REFERENCES reactor_components(id),
    title           TEXT NOT NULL,
    description     TEXT,
    priority        TEXT NOT NULL DEFAULT 'medium',  -- 'critical'|'high'|'medium'|'low'
    status          TEXT NOT NULL DEFAULT 'open',    -- 'open'|'in_progress'|'done'|'deferred'
    source          TEXT NOT NULL DEFAULT 'manual',  -- 'manual'|'schedule'|'predictive'|'alarm'
    assigned_to     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_for   TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    cost_inr        INT,
    parts_used      JSONB,
    sign_off_by     UUID REFERENCES users(id),
    sign_off_notes  TEXT
);
```

### 5.1 Auto-Generated Work Orders

Work orders are created automatically by three triggers:

| Trigger | Source | Example |
|---|---|---|
| Schedule-based | `component_lifecycle_events` past `expected_life_days` | "Enzyme beads due for replenishment in 3 days" |
| Sensor-based | `mesh_fouling_index > 75` from `DP-GAS-01` | "Mesh cartridge fouling — replace within 48h" |
| Predictive | `enzyme_activity_pct < 50` | "Estimated enzyme activity at 47% — replace now" |

### 5.2 API Endpoints

```
GET  /api/plants/{id}/components                  → list all reactor components + health
GET  /api/plants/{id}/components/{key}            → detail + lifecycle history
POST /api/plants/{id}/components/{key}/replace    → record replacement event
GET  /api/plants/{id}/inventory                   → reagent inventory levels
POST /api/plants/{id}/inventory/{reagent}/restock → manual restock entry
GET  /api/plants/{id}/work-orders                 → list open WOs
POST /api/plants/{id}/work-orders                 → create manual WO
PATCH /api/plants/{id}/work-orders/{id}/complete  → sign off completion
GET  /api/plants/{id}/opex-report                 → monthly OPEX breakdown by component
```

---

## 6. OPEX Reporting

```python
def compute_monthly_opex(plant_id: UUID, month: date, db: Session) -> dict:
    """
    Returns OPEX breakdown for the given month:
      - consumables (enzyme, mesh, gases, reagents)
      - labour (hours × rate from work orders)
      - utilities (kWh × tariff from energy meter)
    Compares against economic engine target (annual_opex_inr / 12).
    """
    return {
        "month":       month.isoformat(),
        "enzyme_beads_inr":    ...,
        "mesh_inr":            ...,
        "calibration_gases_inr": ...,
        "ca_oh2_inr":          ...,
        "chitosan_inr":        ...,
        "labour_inr":          ...,
        "utilities_inr":       ...,
        "total_inr":           ...,
        "budget_inr":          ...,   # from economic engine
        "variance_pct":        ...,
    }
```

This feeds the **Executive Dashboard** OPEX trend card directly.

---

## 7. Operator UI — Maintenance Tab

In `packages/web/src/features/operator/`, a new **Maintenance** sub-tab shows:

```
┌────────────────────────────────────────────────────────┐
│ 🔧 Maintenance Overview                                 │
├────────────────────────────────────────────────────────┤
│ Component          │ Health   │ Next Action  │ Due In   │
│ Enzyme Beads       │ 🟡 62%   │ Replenish   │ 6 days   │
│ PP Mesh #1         │ 🟢 18%   │ Monitor     │ 52 days  │
│ EPDM O-Rings       │ 🟢  0%   │ Monitor     │ 4 months │
│ Impeller Coating   │ 🟢 85    │ Monitor     │ 10 months│
├────────────────────────────────────────────────────────┤
│ 📦 Inventory                                            │
│ Ca(OH)₂ slurry     │ 142 L   │ ████████░░ │ 71%      │
│ Chitosan solution  │  38 L   │ ███░░░░░░░ │ 38% ⚠   │
│ N₂ zero gas        │ 0.8 cyl │ █░░░░░░░░░ │ 80% ⚠   │
└────────────────────────────────────────────────────────┘
```

---

## 8. Open Items

| Item | Priority | Owner |
|---|---|---|
| Alembic migration for component + inventory tables | 🔴 High | Platform Eng |
| `lifecycle.py` service + scheduled jobs (Celery Beat) | 🔴 High | Platform Eng |
| Auto-consumption from `FLOW-REG-01` telemetry | 🟡 Medium | Platform Eng |
| Enzyme activity degradation model (lab calibration of k_ref) | 🟡 Medium | Science |
| Maintenance tab in Operator UI | 🟡 Medium | Frontend |
| OPEX report endpoint + executive dashboard card | 🟢 Low | Frontend |
