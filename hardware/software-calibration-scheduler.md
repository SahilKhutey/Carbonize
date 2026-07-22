# Software Specification: Calibration & Preventive Maintenance Scheduler

**Companion to:** [`hardware/calibration-schedule.xlsx`](file:///c:/Users/ASUS/Documents/Carbonize/hardware/calibration-schedule.xlsx) and [`hardware/sensor-stack.md`](file:///c:/Users/ASUS/Documents/Carbonize/hardware/sensor-stack.md) §4 (Auxiliary/Calibration)  
**Owner:** Operator Experience / Platform Engineering  
**Status:** 🟡 Specification Complete — Implementation Pending Pilot Hardware  
**Last updated:** 2026-07-20

---

## 1. Overview

Industrial sensors drift over time and require periodic recalibration. `sensor-stack.md` defines calibration consumables (pH buffers, conductivity standards, zero gas, span gases) and implied maintenance intervals. `calibration-schedule.xlsx` captures the schedule. This document specifies the software that **enforces, tracks, and automates** that schedule within the CBMS platform.

---

## 2. Calibration Intervals (from sensor-stack.md)

| Sensor | Calibration Type | Interval | Consumables |
|---|---|---|---|
| pH (pH-LIQ-01) | 2-point (pH 4.00 + pH 10.00 NIST buffers) | Monthly | pH 4, 7, 10 buffer (₹5K/yr) |
| Conductivity (COND-LIQ-01) | 1-point (1413 μS/cm KCl) | Monthly | KCl standard (₹3K/yr) |
| Dissolved CO₂ (CO2-DIS-01) | Zero + span | Monthly | N₂ zero gas + CO₂ span |
| Dissolved SO₂ (SO2-DIS-01) | Zero + span | Monthly | N₂ zero + SO₂ span |
| DO (DO-LIQ-01) | Air saturation | Monthly | Distilled water |
| ORP (ORP-LIQ-01) | Quinhydrone standard | Quarterly | Quinhydrone solution |
| Turbidity (TURB-LIQ-01) | Formazin standard | Monthly | Formazin 4000 NTU |
| CO₂ NDIR (CO2-GAS-01) | Zero (N₂) + span (12% CO₂) | Monthly | N₂ + CO₂ span gas |
| SO₂ UV (SO2-GAS-01) | Zero + span (50 ppm SO₂) | Quarterly | SO₂ span gas |
| NOₓ CL (NOX-GAS-01) | Zero + span (50 ppm NOₓ) | Quarterly | NOₓ span gas |
| Gas flow (FLOW-GAS-01) | Pitot tube verification | Annually | Calibrated pitot |
| Slurry flow (FLOW-SLR-01) | Gravimetric bucket test | Quarterly | Calibrated bucket |
| PM sensor (PM-GAS-01) | Span filter | Quarterly | Manufacturer kit |

---

## 3. Calibration Event Data Model

The `sensor_calibrations` table (defined in `software-sensor-integration.md`) stores each calibration record. The scheduler layer adds:

```sql
-- Extension to existing calibration tables

CREATE TABLE calibration_schedules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id        UUID NOT NULL REFERENCES plant_profiles(id),
    sensor_id       TEXT NOT NULL,
    cal_type        TEXT NOT NULL,      -- 'zero_span' | 'multipoint' | 'gravimetric' | 'verification'
    interval_days   INT NOT NULL,
    last_cal_date   DATE,
    next_due_date   DATE NOT NULL,
    assigned_to     UUID REFERENCES users(id),
    consumables     JSONB,              -- {"ph_buffer_4": 1, "ph_buffer_10": 1}
    estimated_duration_min INT NOT NULL DEFAULT 30,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE calibration_work_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id     UUID NOT NULL REFERENCES calibration_schedules(id),
    plant_id        UUID NOT NULL,
    sensor_id       TEXT NOT NULL,
    due_date        DATE NOT NULL,
    assigned_to     UUID REFERENCES users(id),
    status          TEXT NOT NULL DEFAULT 'scheduled',  -- scheduled|in_progress|done|skipped
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    -- Results from calibration
    zero_raw        DOUBLE PRECISION,   -- raw reading at zero standard
    zero_expected   DOUBLE PRECISION,
    span_raw        DOUBLE PRECISION,   -- raw reading at span standard
    span_expected   DOUBLE PRECISION,
    computed_offset DOUBLE PRECISION,
    computed_slope  DOUBLE PRECISION,
    r_squared       DOUBLE PRECISION,
    accepted        BOOLEAN,            -- technician sign-off
    rejection_reason TEXT,
    calibration_record_id UUID REFERENCES sensor_calibrations(id)
);
```

---

## 4. Calibration Engine — Curve Fitting

```python
# packages/api/src/cbms_api/services/calibration_engine.py

import numpy as np
from scipy.stats import linregress

def fit_two_point_calibration(
    raw_readings: list[float],
    known_values:  list[float],
) -> dict:
    """
    Fits a linear calibration: corrected = slope × raw + offset
    Returns slope, offset, R².
    Accepts 2 or more calibration points.
    """
    if len(raw_readings) < 2:
        raise ValueError("At least 2 calibration points required")

    slope, offset, r_value, _, _ = linregress(raw_readings, known_values)
    return {
        "slope":     round(slope, 6),
        "offset":    round(offset, 4),
        "r_squared": round(r_value ** 2, 6),
    }


def evaluate_calibration_quality(result: dict, sensor_id: str) -> tuple[bool, list[str]]:
    """
    Checks whether the fitted calibration meets quality thresholds.
    Returns (is_acceptable, [warning messages])
    """
    warnings = []
    THRESHOLDS = {
        "pH-LIQ-01":   {"min_r2": 0.9990, "max_offset": 0.5,  "max_slope_dev": 0.05},
        "CO2-GAS-01":  {"min_r2": 0.9990, "max_offset": 0.5,  "max_slope_dev": 0.05},
        "SO2-GAS-01":  {"min_r2": 0.9980, "max_offset": 5.0,  "max_slope_dev": 0.10},
        "NOX-GAS-01":  {"min_r2": 0.9980, "max_offset": 5.0,  "max_slope_dev": 0.10},
        "_default":    {"min_r2": 0.9950, "max_offset": 10.0, "max_slope_dev": 0.15},
    }
    t = THRESHOLDS.get(sensor_id, THRESHOLDS["_default"])

    if result["r_squared"] < t["min_r2"]:
        warnings.append(f"R² {result['r_squared']:.4f} < required {t['min_r2']}")

    if abs(result["offset"]) > t["max_offset"]:
        warnings.append(
            f"Offset {result['offset']:.3f} exceeds threshold {t['max_offset']} — "
            "check sensor fouling or damage"
        )

    slope_dev = abs(result["slope"] - 1.0)
    if slope_dev > t["max_slope_dev"]:
        warnings.append(
            f"Slope {result['slope']:.4f} deviates {slope_dev:.3f} from 1.0 — "
            "check calibration standard"
        )

    is_acceptable = len(warnings) == 0
    return is_acceptable, warnings
```

---

## 5. Automated Schedule Management

### 5.1 Daily Schedule Check (Celery Beat)

```python
# Runs every day at 06:00 plant local time

@shared_task(name="tasks.check_calibration_schedules")
async def check_calibration_schedules():
    """
    For each active calibration schedule:
      - If next_due_date is within 7 days → create CalibrationWorkOrder
      - If next_due_date has passed and no WO completed → escalate to operator
      - Sends reminder notifications via email/webhook
    """
    today = date.today()
    for schedule in await get_active_schedules():
        days_until_due = (schedule.next_due_date - today).days
        if days_until_due <= 7:
            await create_calibration_work_order(schedule)
        if days_until_due < 0 and not await has_completed_wo(schedule):
            await escalate_overdue_calibration(schedule)
```

### 5.2 Next Due Date Computation

```python
def compute_next_due(last_cal_date: date, interval_days: int) -> date:
    """
    Standard: next_due = last_cal_date + interval_days
    If never calibrated: next_due = install_date + interval_days
    Clamp to never be in the past from today.
    """
    next_due = last_cal_date + timedelta(days=interval_days)
    return max(next_due, date.today())
```

---

## 6. Calibration Procedure Guides (in-app)

Each sensor has a step-by-step calibration procedure rendered in the Operator UI:

```python
CALIBRATION_PROCEDURES = {
    "pH-LIQ-01": {
        "title":    "pH Sensor 2-Point Calibration",
        "duration": 30,
        "steps": [
            "1. Remove sensor from reactor. Rinse with DI water.",
            "2. Immerse in pH 4.00 NIST buffer for 3 min. Record stable reading.",
            "3. Rinse with DI water. Immerse in pH 10.00 NIST buffer for 3 min. Record.",
            "4. Enter both readings in the calibration form below.",
            "5. System will compute slope + offset and display R².",
            "6. If R² ≥ 0.999, accept. Reinstall sensor.",
            "7. Refill reference KCl solution if low (<25% full).",
        ],
        "standards_required": ["pH 4.00 NIST buffer", "pH 10.00 NIST buffer"],
        "accept_threshold":   {"r_squared": 0.9990},
    },
    "CO2-GAS-01": {
        "title":    "LI-840A CO₂ Analyser Zero-Span Calibration",
        "duration": 45,
        "steps": [
            "1. Connect N₂ zero gas cylinder to analyser inlet. Open valve.",
            "2. Allow 5 min purge. Record stable zero reading (should be 0.00 ± 0.05 vol%).",
            "3. Switch to 12% CO₂ span gas cylinder.",
            "4. Allow 5 min stabilisation. Record stable reading.",
            "5. Enter zero + span readings below.",
            "6. Accept if R² ≥ 0.999 and offset < 0.5 vol%.",
            "7. Log N₂ cylinder usage (approx 0.5 bar consumed per calibration).",
        ],
        "standards_required": ["N₂ 99.999% zero gas", "CO₂ 12% in N₂ span gas"],
        "accept_threshold":   {"r_squared": 0.9990, "max_offset": 0.5},
    },
    # ... one procedure per sensor
}
```

---

## 7. Calibration Certificate Generation

On completion and acceptance of a calibration work order, the system generates a NIST-traceable calibration certificate:

```python
def render_calibration_certificate(wo: CalibrationWorkOrder) -> dict:
    return {
        "certificate_id":  str(wo.id)[:8].upper(),
        "sensor_id":       wo.sensor_id,
        "plant_id":        str(wo.plant_id),
        "calibrated_at":   wo.completed_at.isoformat(),
        "calibrated_by":   wo.assigned_to_name,
        "standards_used":  wo.consumables,
        "zero_reading":    wo.zero_raw,
        "zero_expected":   wo.zero_expected,
        "span_reading":    wo.span_raw,
        "span_expected":   wo.span_expected,
        "slope":           wo.computed_slope,
        "offset":          wo.computed_offset,
        "r_squared":       wo.r_squared,
        "result":          "ACCEPTED" if wo.accepted else "REJECTED",
        "next_due_date":   (wo.completed_at.date()
                            + timedelta(days=_get_interval(wo.sensor_id))).isoformat(),
        "traceability":    "NIST pH 4.00, 10.00 / NIST KCl 1413 μS/cm",
    }
```

Certificates are downloadable as PDF and stored against the calibration record for auditor access.

---

## 8. Calibration Status Dashboard (Operator UI)

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔬 Calibration Status — Pune Alpha Plant                          │
├──────────────────────────────────────────────────────────────────┤
│ Sensor          │ Last Cal   │ Next Due   │ Days  │ Status       │
│ pH (AT-101)     │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ Conductivity    │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ Dissolved CO₂   │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ Dissolved SO₂   │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ CO₂ NDIR        │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ SO₂ UV          │ 2026-04-01 │ 2026-07-01 │  −19d │ 🔴 OVERDUE  │
│ NOₓ CL          │ 2026-04-01 │ 2026-07-01 │  −19d │ 🔴 OVERDUE  │
│ ORP             │ 2026-05-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ Turbidity       │ 2026-07-01 │ 2026-08-01 │ +12d  │ 🟢 Current  │
│ Gas flow        │ 2026-01-15 │ 2027-01-15 │ +179d │ 🟢 Current  │
├──────────────────────────────────────────────────────────────────┤
│ 📦 Calibration Gas Inventory                                      │
│ N₂ zero gas     │ 0.3 cylinder │ ████░░░░░░ │ 30% ⚠ Low        │
│ CO₂ 12% span    │ 0.7 cylinder │ ████████░░ │ 70%              │
│ SO₂ 50ppm span  │ 0.9 cylinder │ █████████░ │ 90%              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 9. API Endpoints

```
GET  /api/plants/{id}/calibration/schedule            → full calibration calendar
GET  /api/plants/{id}/calibration/work-orders         → open + completed WOs
POST /api/plants/{id}/calibration/work-orders/{id}/start     → begin calibration
POST /api/plants/{id}/calibration/work-orders/{id}/record    → enter results + compute fit
POST /api/plants/{id}/calibration/work-orders/{id}/accept    → technician sign-off
GET  /api/plants/{id}/calibration/work-orders/{id}/certificate → download cert PDF
GET  /api/plants/{id}/calibration/procedures/{sensor_id}     → step-by-step guide
GET  /api/plants/{id}/calibration/status                     → summary dashboard data
```

---

## 10. Compliance & Audit Trail

All calibration events are immutable and audit-trailed:

- `calibration_work_orders` rows are never deleted — only marked complete/skipped
- Each accepted calibration pushes a signed entry to `sensor_calibrations`
- Overdue calibrations (`next_due_date < today`) automatically set the affected sensor's quality code to `CAL_REQUIRED` via the sensor driver
- Monthly audit CSV export available for CPCB/MoEFCC compliance reporting

---

## 11. Open Items

| Item | Priority | Owner |
|---|---|---|
| Alembic migration for calibration_schedules + calibration_work_orders | 🔴 High | Platform Eng |
| `check_calibration_schedules` Celery Beat task | 🔴 High | Platform Eng |
| `fit_two_point_calibration` + `evaluate_calibration_quality` | 🔴 High | Platform Eng |
| All sensor calibration procedures (CALIBRATION_PROCEDURES dict) | 🟡 Medium | Science + Platform Eng |
| Calibration certificate PDF template (WeasyPrint) | 🟡 Medium | Platform Eng |
| Calibration status dashboard UI in Operator → Maintenance | 🟡 Medium | Frontend |
| Calibration gas inventory tracking (link to reagent inventory) | 🟡 Medium | Platform Eng |
| CPCB audit export endpoint | 🟢 Low | Platform Eng |
