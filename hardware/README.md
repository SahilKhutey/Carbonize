# Hardware ↔ Software Cross-Reference Index

**Carbonize CBMS — Hardware Section Software Documents**  
**Last updated:** 2026-07-20

This document is the master index linking each hardware specification to its corresponding software specification. Every physical component in the CBMS pilot reactor has a software counterpart that handles data ingestion, lifecycle tracking, calibration management, and safety enforcement.

---

## Document Map

| Hardware Document | Software Companion | Description |
|---|---|---|
| [`sensor-stack.md`](sensor-stack.md) | [`software-sensor-integration.md`](software-sensor-integration.md) | Sensor registry, MQTT topics, Modbus/RS-232 drivers, calibration engine, quality guard |
| [`daq-architecture.md`](daq-architecture.md) | [`software-daq-edge-cloud.md`](software-daq-edge-cloud.md) | PLC register map, Pi gateway, InfluxDB ring buffer, cloud sync, OTA, Prometheus metrics |
| [`materials-spec.md`](materials-spec.md) | [`software-lifecycle-tracking.md`](software-lifecycle-tracking.md) | Component registry, consumable schedules, predictive wear models, work orders, OPEX reporting |
| [`corrosion-test-protocol.md`](corrosion-test-protocol.md) | [`software-corrosion-test-pipeline.md`](software-corrosion-test-pipeline.md) | Specimen registry, inspection scheduling, pass/fail evaluation, procurement gate, qualification reports |
| [`calibration-schedule.xlsx`](calibration-schedule.xlsx) | [`software-calibration-scheduler.md`](software-calibration-scheduler.md) | Calibration intervals, curve fitting, Celery Beat reminders, certificate generation, CPCB audit trail |

---

## End-to-End Data Flow

```
Physical Sensor
      │  (4-20mA / Modbus / RS-232)
      ▼
PLC / NI cDAQ  ←─── Safety interlocks (ladder logic, NOT software)
      │  (Modbus TCP)
      ▼
Raspberry Pi Gateway  ←─── cbms-gateway (Python systemd service)
  ├── CalibrationEngine  (offset + slope from latest sensor_calibration)
  ├── QualityGuard       (range, rate-of-change, stuck detection)
  ├── LocalInfluxDB      (72h ring buffer, offline resilience)
  └── CloudSyncer        (batch → gzip → POST /api/ingest/telemetry)
      │  (HTTPS + JWT device token)
      ▼
CBMS Cloud API (FastAPI)
  ├── /api/ingest/telemetry  → writes to InfluxDB Cloud
  ├── AlertEvaluator         → PostgreSQL alarm records + WebSocket push
  ├── LifecycleService       → consumable wear + work orders
  └── CalibrationService     → calibration work orders + schedule
      │
      ▼
Frontend (React + TypeScript)
  ├── digital-twin/    ← live P&ID overlay with sensor values
  ├── operator/        ← alarms, shift handover, maintenance tab
  └── executive/       ← OPEX trends, asset health KPIs
```

---

## Key Shared Database Tables

| Table | Spec | Purpose |
|---|---|---|
| `sensor_calibrations` | sensor-integration | Latest approved calibration per sensor |
| `sensor_faults` | sensor-integration | Quality fault log |
| `calibration_schedules` | calibration-scheduler | Per-sensor calibration intervals |
| `calibration_work_orders` | calibration-scheduler | Individual calibration events + results |
| `reactor_components` | lifecycle-tracking | Component registry + expected lifetime |
| `component_lifecycle_events` | lifecycle-tracking | Replacement, inspection, failure history |
| `maintenance_work_orders` | lifecycle-tracking | Predictive + scheduled maintenance WOs |
| `reagent_inventory` | lifecycle-tracking | Ca(OH)₂, chitosan, calibration gas levels |
| `reagent_consumption_log` | lifecycle-tracking | Auto-decremented from flow meter readings |
| `corrosion_tests` | corrosion-pipeline | 30-day material qualification runs |
| `corrosion_specimens` | corrosion-pipeline | Individual material coupons under test |
| `corrosion_inspections` | corrosion-pipeline | Per-day inspection measurements |

---

## Critical Path — Software Before Pilot Hardware Arrives

The following software items must be complete **before** the pilot reactor is switched on. Nothing else is blocked:

| Priority | Item | Spec Doc |
|---|---|---|
| 🔴 P0 | `cbms-gateway` Python package + systemd service | daq-edge-cloud |
| 🔴 P0 | `ModbusDriver` + `RS232Driver` implementations | sensor-integration |
| 🔴 P0 | `POST /api/ingest/telemetry` endpoint | daq-edge-cloud |
| 🔴 P0 | Device JWT auth (`/api/auth/device`) | daq-edge-cloud |
| 🔴 P0 | InfluxDB Cloud bucket + write path | daq-edge-cloud |
| 🔴 P0 | `sensor_calibrations` Alembic migration | sensor-integration |
| 🔴 P0 | `reactor_components` + lifecycle Alembic migrations | lifecycle-tracking |
| 🔴 P1 | `QualityGuard` rule engine | sensor-integration |
| 🔴 P1 | Corrosion test tables + evaluation service | corrosion-pipeline |
| 🔴 P1 | Calibration schedule + work order tables | calibration-scheduler |
| 🟡 P2 | Digital Twin WebSocket `SENSOR_UPDATE` messages | daq-edge-cloud |
| 🟡 P2 | Maintenance tab in Operator UI | lifecycle-tracking |
| 🟡 P2 | Calibration status dashboard | calibration-scheduler |
| 🟡 P2 | Corrosion test tracker UI | corrosion-pipeline |
| 🟢 P3 | OTA update mechanism (A/B partition) | daq-edge-cloud |
| 🟢 P3 | Qualification report PDF generation | corrosion-pipeline |
| 🟢 P3 | CPCB audit export | calibration-scheduler |

---

## Sensor → Model Validation Dependency

The 5 sensors that gate model validation (per `sensor-stack.md` §"Critical Metrics"):

| Sensor | `sensor_id` | Validates | Software Gate |
|---|---|---|---|
| Dissolved CO₂ | `CO2-DIS-01` | k_cat (CA activity) | `validation_data_quality = INSUFFICIENT` if GOOD < 5 min |
| Dissolved SO₂ | `SO2-DIS-01` | k_so2_abs | Same gate |
| Gas-phase CO₂ | `CO2-GAS-01` | Overall capture rate | Same gate (2 min timeout) |
| Turbidity | `TURB-LIQ-01` | CaCO₃ precipitation | Same gate (5 min timeout) |
| pH | `pH-LIQ-01` | Alkalinity budget | Same gate (10 min timeout) |

When any of these report `quality ≠ GOOD` for longer than the timeout, the simulation worker sets the run's `validation_data_quality = INSUFFICIENT` and the Sobol / UQ analysis is blocked from running — preventing false-precision results from bad sensor data.

---

## Cost Summary (Software Infrastructure)

| Layer | Component | Est. Monthly Cost (USD) |
|---|---|---|
| Edge | Raspberry Pi 5 + 4G SIM | $15–25/plant/month |
| Cloud | InfluxDB Cloud (Starter) | $0 up to 10K writes/s |
| Cloud | InfluxDB Cloud (Production, 50GB) | $~50/month |
| Cloud | PostgreSQL (Supabase / RDS t3.micro) | $~25/month |
| Cloud | Redis (Celery broker, ElastiCache t3.micro) | $~20/month |
| CDN | OTA update tarball hosting (S3) | $~1/month |
| **Total** | **Single-plant pilot** | **~$110/month** |

This is well within the operational budget modelled by the economic engine.
