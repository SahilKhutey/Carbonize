# Software Specification: Sensor Integration & Driver Layer

**Companion to:** [`sensor-stack.md`](sensor-stack.md)  
**Owner:** Platform Engineering  
**Status:** 🟡 Specification Complete — Implementation Pending Pilot Hardware  
**Last updated:** 2026-07-20

---

## 1. Overview

This document specifies the software layer that sits between the physical sensor stack and the CBMS platform. Every sensor listed in `sensor-stack.md` must be represented in software as a typed data stream with validated units, calibration state, and quality flags. The software layer is responsible for:

- Parsing raw sensor telegrams (4-20 mA, Modbus RTU/TCP, HART, RS-232)
- Applying calibration offsets and linearisation curves
- Emitting validated readings as time-stamped, unit-tagged MQTT messages
- Raising quality alerts when sensors drift outside calibration bounds or go offline

---

## 2. Sensor Registry

Every deployed sensor is registered in the database at provisioning time. The schema:

```python
# packages/sim-core/src/cbms_sim/hardware/sensor_registry.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Protocol(str, Enum):
    MODBUS_RTU  = "modbus_rtu"
    MODBUS_TCP  = "modbus_tcp"
    ANALOG_420  = "4_20mA"
    HART        = "hart"
    RS232       = "rs232"
    MQTT        = "mqtt"

class SensorPhase(str, Enum):
    LIQUID = "liquid"
    GAS    = "gas"
    FLOW   = "flow"
    AUX    = "auxiliary"

@dataclass
class SensorSpec:
    sensor_id:       str               # e.g. "pH-01", "CO2-GAS-01"
    tag:             str               # P&ID tag (e.g. "AT-101")
    description:     str
    phase:           SensorPhase
    unit:            str               # SI unit string, e.g. "pH", "mg/L", "Nm3/hr"
    range_min:       float
    range_max:       float
    accuracy_pct:    float             # % of reading
    sample_rate_hz:  float             # 0.1 → 10 Hz
    max_latency_ms:  int
    protocol:        Protocol
    address:         str               # e.g. "192.168.1.10:502" or "/dev/ttyUSB0:1"
    register_start:  Optional[int] = None
    calibration_due: Optional[str] = None  # ISO date
    part_number:     Optional[str] = None
    cost_inr:        Optional[int] = None
```

### 2.1 Registered Sensors (matching sensor-stack.md)

| `sensor_id` | Tag | Phase | Unit | Rate (Hz) | Protocol | Part No. |
|---|---|---|---|---|---|---|
| `pH-LIQ-01` | AT-101 | liquid | pH | 0.1 | Modbus TCP | 52003887 |
| `COND-LIQ-01` | AT-102 | liquid | mS/cm | 0.1 | Modbus TCP | 52003890 |
| `TEMP-LIQ-01` | TT-101 | liquid | °C | 1.0 | 4-20mA | TR10-AAA1A |
| `TEMP-GAS-01` | TT-102 | gas | °C | 1.0 | 4-20mA | TR10-AAA1A |
| `CO2-DIS-01` | AT-103 | liquid | mg/L | 0.1 | Modbus TCP | 30039031 |
| `SO2-DIS-01` | AT-104 | liquid | mg/L | 0.1 | RS-232 | 9184SC |
| `DO-LIQ-01` | AT-105 | liquid | mg/L | 0.5 | Modbus TCP | LDO10101 |
| `ORP-LIQ-01` | AT-106 | liquid | mV | 0.5 | Modbus TCP | 52003893 |
| `TURB-LIQ-01` | AT-107 | liquid | NTU | 0.5 | Modbus TCP | SOLITAXSC |
| `CO2-GAS-01` | AT-201 | gas | vol% | 1.0 | RS-232 | LI-840A |
| `SO2-GAS-01` | AT-202 | gas | ppm | 0.1 | RS-232 | 43iQ |
| `NOX-GAS-01` | AT-203 | gas | ppb | 0.1 | RS-232 | 42iQ |
| `FLOW-GAS-01` | FT-201 | gas | Nm³/hr | 10.0 | Modbus TCP | Prowirl 200 |
| `DP-GAS-01` | PDT-201 | gas | mbar | 10.0 | 4-20mA | PMD55B |
| `PM-GAS-01` | AT-204 | gas | mg/Nm³ | 0.1 | RS-232 | FW100 |
| `FLOW-SLR-01` | FT-101 | flow | L/min | 10.0 | Modbus TCP | Promag P100 |
| `FLOW-REG-01` | FT-102 | flow | L/min | 10.0 | Modbus TCP | M13V14I |

---

## 3. Driver Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SensorDriverManager                        │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ ModbusDriver  │  │  AnalogDriver  │  │  RS232Driver   │  │
│  │ (TCP + RTU)   │  │  (NI 9208 AI) │  │  (LI-840A etc) │  │
│  └───────┬───────┘  └───────┬────────┘  └───────┬────────┘  │
│          └──────────────────┴───────────────────┘            │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │  CalibrationEngine  │                         │
│              │  (offset + slope)   │                         │
│              └──────────┬──────────┘                         │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │   QualityGuard      │                         │
│              │  (range, rate-of-   │                         │
│              │   change, stuck)    │                         │
│              └──────────┬──────────┘                         │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │   MQTT Publisher    │                         │
│              │  cbms/plant/{id}/   │                         │
│              │  sensor/{tag}       │                         │
│              └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 MQTT Topic Schema

All sensor readings are published on:

```
cbms/plant/{plant_id}/sensor/{sensor_id}
```

**Payload (JSON):**
```json
{
  "ts":        "2026-07-20T14:32:01.123Z",
  "sensor_id": "CO2-GAS-01",
  "tag":       "AT-201",
  "value":     14.72,
  "unit":      "vol%",
  "quality":   "GOOD",
  "raw_counts": 17841,
  "cal_offset": -0.12,
  "cal_slope":  1.003
}
```

**Quality codes:**

| Code | Meaning |
|---|---|
| `GOOD` | Within range, passing all checks |
| `UNCERTAIN` | Recent calibration expired or signal drift detected |
| `BAD_RANGE` | Value outside physical sensor range |
| `BAD_STUCK` | No change in value for > 5× sample interval |
| `BAD_COMMS` | Driver lost connection; last value age > 60 s |
| `CAL_REQUIRED` | Calibration due within 7 days |

### 3.2 Calibration Engine

```python
@dataclass
class CalibrationRecord:
    sensor_id:    str
    applied_at:   datetime
    offset:       float    # added to raw reading
    slope:        float    # raw reading × slope
    r_squared:    float    # from calibration curve fit
    next_due:     datetime
    technician:   str
    std_solution: str      # e.g. "pH 4.00 NIST"

def apply_calibration(raw: float, cal: CalibrationRecord) -> float:
    """Corrected = (raw × slope) + offset"""
    return (raw * cal.slope) + cal.offset
```

Calibration records are stored in the `sensor_calibrations` table and fetched at driver startup. The engine:
- Loads the most recent approved calibration per sensor on startup
- Applies `corrected = (raw × slope) + offset`
- Sets `quality = CAL_REQUIRED` when `next_due - now() < 7 days`

---

## 4. Modbus Driver (Primary)

Handles Mettler-Toledo InPro series, Endress+Hauser Promag/Deltabar, Hach LDO.

```python
# packages/workers/src/cbms_workers/hardware/drivers/modbus_driver.py

import asyncio
from pymodbus.client import AsyncModbusTcpClient

class ModbusDriver:
    POLL_INTERVAL_S = {
        "pH-LIQ-01":    10.0,
        "COND-LIQ-01":  10.0,
        "CO2-DIS-01":   10.0,
        "DO-LIQ-01":    2.0,
        "TURB-LIQ-01":  2.0,
        "FLOW-GAS-01":  0.1,
        "FLOW-SLR-01":  0.1,
    }

    async def poll_loop(self, spec: SensorSpec) -> AsyncIterator[RawReading]:
        client = AsyncModbusTcpClient(spec.address)
        await client.connect()
        interval = self.POLL_INTERVAL_S.get(spec.sensor_id, 1.0)
        while True:
            result = await client.read_holding_registers(
                spec.register_start, count=2
            )
            raw = self._decode_float32(result.registers)
            yield RawReading(sensor_id=spec.sensor_id, raw=raw,
                             ts=datetime.now(UTC))
            await asyncio.sleep(interval)
```

---

## 5. RS-232 Driver (Gas Analysers)

Handles LI-COR LI-840A (CO₂ NDIR), Thermo 43iQ (SO₂), Thermo 42iQ (NOₓ), Sick FW100 (PM).

```python
class RS232Driver:
    """
    Each analyser has a proprietary ASCII protocol.
    LI-840A: outputs '<li840><data><co2>14.72</co2>...'  (XML, 1 Hz)
    Thermo 43iQ: outputs 'SO2  0.872 ppm' (space-delimited, 0.1 Hz)
    Thermo 42iQ: outputs 'NO  12.3 NOX  14.1 ppb' (space-delimited, 0.1 Hz)
    """
    PARSERS = {
        "CO2-GAS-01": "_parse_licor_xml",
        "SO2-GAS-01": "_parse_thermo_space",
        "NOX-GAS-01": "_parse_thermo_nox",
        "PM-GAS-01":  "_parse_sick_fw100",
    }
```

---

## 6. Quality Guard Rules

```python
QUALITY_RULES = {
    "pH-LIQ-01": {
        "range":           (4.0, 12.0),
        "rate_of_change":  0.5,          # max pH units/minute
        "stuck_threshold": 0.001,         # min variation over 5 min
    },
    "CO2-GAS-01": {
        "range":           (0.0, 20.0),   # vol%
        "rate_of_change":  5.0,           # max vol%/minute
        "stuck_threshold": 0.01,
    },
    "FLOW-SLR-01": {
        "range":           (0.0, 50.0),   # L/min
        "rate_of_change":  10.0,
        "stuck_threshold": 0.1,
    },
    # ... one rule per sensor_id
}
```

---

## 7. Sensor Data Persistence

### 7.1 InfluxDB Schema (time-series)

```
measurement: sensor_reading
tags:        plant_id, sensor_id, tag, unit, quality
fields:      value (float), raw_counts (int), cal_offset (float), cal_slope (float)
timestamp:   nanosecond precision
```

Retention policy: 90 days full resolution → downsampled to 1-min averages for 2 years.

### 7.2 PostgreSQL (calibration state)

```sql
CREATE TABLE sensor_calibrations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    sensor_id       TEXT NOT NULL,
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    offset_val      DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    slope_val       DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    r_squared       DOUBLE PRECISION,
    next_due        TIMESTAMPTZ NOT NULL,
    technician      TEXT,
    std_solution    TEXT,
    notes           TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE sensor_faults (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id    UUID NOT NULL,
    sensor_id   TEXT NOT NULL,
    fault_code  TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    auto_resolved BOOLEAN DEFAULT FALSE
);
```

---

## 8. Critical Sensor Validation Thresholds

Per `sensor-stack.md` § "Critical Metrics for Model Validation", these 5 sensors gate the model validation run:

| Sensor | Model Parameter | Alert if |
|---|---|---|
| `CO2-DIS-01` | k_cat (CA activity) | quality ≠ GOOD for > 5 min |
| `SO2-DIS-01` | k_so2_abs | quality ≠ GOOD for > 5 min |
| `CO2-GAS-01` | Overall capture rate | quality ≠ GOOD for > 2 min |
| `TURB-LIQ-01` | CaCO₃ precipitation | quality ≠ GOOD for > 5 min |
| `pH-LIQ-01` | Alkalinity budget | quality ≠ GOOD for > 10 min |

When any of these triggers, the simulation worker sets `validation_data_quality = INSUFFICIENT` and blocks the Sobol analysis from running — preventing false-precision results from bad sensor data.

---

## 9. API Endpoints

```
GET  /api/plants/{id}/sensors                → list all registered sensors + current status
GET  /api/plants/{id}/sensors/{sensor_id}    → latest reading + calibration state
POST /api/plants/{id}/sensors/{sensor_id}/calibrate  → record a new calibration event
GET  /api/plants/{id}/sensors/{sensor_id}/history    → time-series (InfluxDB proxy)
POST /api/plants/{id}/sensors/{sensor_id}/fault      → manually log a fault
```

---

## 10. Open Items

| Item | Priority | Owner |
|---|---|---|
| Implement `ModbusDriver` poll loop + reconnect logic | 🔴 High | Platform Eng |
| Implement `RS232Driver` for LI-840A XML parser | 🔴 High | Platform Eng |
| Write Alembic migration for `sensor_calibrations` + `sensor_faults` tables | 🔴 High | Platform Eng |
| Implement `QualityGuard` rule engine | 🟡 Medium | Platform Eng |
| Wire `validation_data_quality` flag into simulation task | 🟡 Medium | Sim Core |
| Add InfluxDB client to `cbms_workers` | 🟡 Medium | Platform Eng |
| Unit tests for calibration math | 🟡 Medium | QA |
