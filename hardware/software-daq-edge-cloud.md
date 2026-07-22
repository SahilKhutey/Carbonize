# Software Specification: DAQ Edge Software & Cloud Ingestion Pipeline

**Companion to:** [`hardware/daq-architecture.md`](file:///c:/Users/ASUS/Documents/Carbonize/hardware/daq-architecture.md)  
**Owner:** Platform Engineering / DevOps  
**Status:** 🟡 Specification Complete — Implementation Pending Pilot Hardware  
**Last updated:** 2026-07-20

---

## 1. Overview

The physical DAQ layer (NI cDAQ-9189 + Siemens S7-1200 + Raspberry Pi 5 gateway) produces raw sensor data at rates between 0.1 Hz and 10 Hz. This document specifies all software running at each tier of that stack:

```
[Physical Sensors] → [PLC/cDAQ Edge] → [Pi Gateway] → [CBMS Cloud API]
                          (Tier 1)          (Tier 2)        (Tier 3)
```

---

## 2. Tier 1 — PLC Edge Logic (Siemens S7-1200)

### 2.1 Responsibilities

- Read analog input channels from NI 9208 modules via OPC-UA
- Execute safety interlocks (hard-coded ladder logic, independent of software)
- Scale raw counts (4-20 mA) to engineering units
- Write scaled values to Modbus holding registers for gateway polling

### 2.2 Modbus Register Map

The S7-1200 exposes a Modbus TCP server on port 502. The Pi gateway polls this map:

| Register | Sensor | Scale | Unit |
|---|---|---|---|
| 40001–40002 | pH (float32 big-endian) | 0–14 | pH |
| 40003–40004 | Conductivity | 0–50 | mS/cm |
| 40005–40006 | Temp (liquid) | 0–100 | °C |
| 40007–40008 | Temp (gas) | 0–100 | °C |
| 40009–40010 | Dissolved CO₂ | 0–500 | mg/L |
| 40011–40012 | Dissolved SO₂ | 0–2000 | mg/L |
| 40013–40014 | Dissolved O₂ | 0–20 | mg/L |
| 40015–40016 | ORP | −2000–+2000 | mV |
| 40017–40018 | Turbidity | 0–4000 | NTU |
| 40019–40020 | Gas flow | 0–100 | Nm³/hr |
| 40021–40022 | Gas ΔP | 0–100 | mbar |
| 40023–40024 | Slurry flow | 0–50 | L/min |
| 40025–40026 | Reagent flow | 0–10 | L/min |
| 40100 | Alarm word (uint16 bit-flags) | — | — |
| 40101 | Watchdog counter (increments 1/s) | — | count |

### 2.3 Safety Interlock Logic (PLC Ladder — NOT software-overrideable)

```
IF pH < 6.0 THEN EMERGENCY_STOP → close inlet valve (YV-101)
IF pH > 12.0 THEN ALARM_HIGH_PH → alert operator, reduce reagent feed
IF reactor_pressure > 1.15 bar THEN OPEN_RELIEF_VALVE (PRV-201)
IF temp_liquid > 58°C THEN SHUTDOWN_HEATER + OPEN_COOLING_VALVE
IF gas_flow = 0 AND fan_running THEN FAN_FAULT_ALARM
```

These interlocks execute entirely on the PLC at scan cycle < 10 ms. The cloud software **cannot override** them — this is a hard safety boundary.

---

## 3. Tier 2 — Raspberry Pi 5 Edge Gateway

### 3.1 Software Stack

```
OS:            Raspberry Pi OS Lite (64-bit, bookworm)
Runtime:       Python 3.12 (uv-managed venv)
Services:      cbms-gateway (systemd), influxd (local InfluxDB), mosquitto (MQTT broker)
Connectivity:  4G LTE (primary), Ethernet (backup)
Local storage: 64 GB microSD → buffered writes during outage
Watchdog:      Hardware WDT enabled (Pi BCM2712 watchdog)
```

### 3.2 Gateway Process Architecture

```
cbms-gateway (systemd process)
    ├── ModbusPoller          — polls S7-1200 every 100ms, 1s, 10s per schedule
    ├── RS232Poller           — reads LI-840A, 43iQ, 42iQ, FW100 via serial
    ├── CalibrationEngine     — applies stored offset/slope per sensor
    ├── QualityGuard          — validates range, rate-of-change, stuck detection
    ├── LocalInfluxWriter     — writes all readings to local InfluxDB (ring buffer)
    ├── MQTTPublisher         — publishes to local mosquitto broker
    └── CloudSyncer           — batches + forwards to CBMS API when online
```

### 3.3 Poll Schedule

```python
# packages/workers/src/cbms_workers/hardware/gateway/poll_schedule.py

POLL_GROUPS = {
    "fast":   {"interval_ms": 100,  "sensors": ["FLOW-GAS-01", "DP-GAS-01", "FLOW-SLR-01"]},
    "medium": {"interval_ms": 1000, "sensors": ["TEMP-LIQ-01", "TEMP-GAS-01", "CO2-GAS-01", "DO-LIQ-01", "ORP-LIQ-01", "TURB-LIQ-01"]},
    "slow":   {"interval_ms": 10000,"sensors": ["pH-LIQ-01", "COND-LIQ-01", "CO2-DIS-01", "SO2-DIS-01", "SO2-GAS-01", "NOX-GAS-01", "PM-GAS-01"]},
}
```

### 3.4 Local InfluxDB Ring Buffer

```
database:    cbms_local
retention:   72h (3 days offline buffer)
precision:   ms
measurement: sensor_reading
tags:        sensor_id, plant_id, quality
fields:      value, raw_counts, cal_offset, cal_slope
```

This ensures no data loss during network outages up to 72 hours.

### 3.5 Cloud Sync Protocol

```python
class CloudSyncer:
    """
    Batches unsynced InfluxDB rows → POST /api/ingest/telemetry
    On ACK from cloud: marks rows as synced
    On failure: exponential backoff (1s → 2s → 4s → max 5min)
    Batch size: 500 rows
    Compression: gzip
    Auth: Bearer token (JWT, rotated every 24h via /api/auth/device)
    """
    ENDPOINT    = "https://api.cbms.app/api/ingest/telemetry"
    BATCH_SIZE  = 500
    MAX_BACKOFF = 300  # seconds
```

### 3.6 Edge Config File

```yaml
# /etc/cbms-gateway/config.yaml
plant_id: "plant-uuid-goes-here"
api_base: "https://api.cbms.app"
api_key:  "${CBMS_DEVICE_API_KEY}"   # from /etc/cbms-gateway/.env (600 perms)

modbus:
  host: "192.168.1.10"
  port: 502
  timeout_s: 2
  reconnect_interval_s: 5

serial_ports:
  CO2-GAS-01: { port: "/dev/ttyUSB0", baud: 9600, protocol: licor_xml }
  SO2-GAS-01: { port: "/dev/ttyUSB1", baud: 9600, protocol: thermo_space }
  NOX-GAS-01: { port: "/dev/ttyUSB2", baud: 9600, protocol: thermo_nox }
  PM-GAS-01:  { port: "/dev/ttyUSB3", baud: 9600, protocol: sick_fw100 }

mqtt:
  broker: "localhost"
  port: 1883
  qos: 1

influx:
  url:      "http://localhost:8086"
  token:    "${INFLUX_TOKEN}"
  org:      "cbms"
  bucket:   "cbms_local"
  retention: "72h"

watchdog:
  enabled: true
  timeout_s: 30
  pet_interval_s: 10
```

### 3.7 Systemd Unit

```ini
[Unit]
Description=CBMS Edge Gateway
After=network-online.target influxd.service mosquitto.service
Wants=network-online.target

[Service]
User=cbms
WorkingDirectory=/opt/cbms-gateway
ExecStart=/opt/cbms-gateway/.venv/bin/python -m cbms_gateway.main
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
WatchdogSec=60s
NotifyAccess=main
# Hardware watchdog via systemd
WatchdogDevice=/dev/watchdog

[Install]
WantedBy=multi-user.target
```

---

## 4. Tier 3 — CBMS Cloud API Ingestion

### 4.1 Telemetry Ingestion Endpoint

```python
# packages/api/src/cbms_api/api/routes/telemetry.py

@router.post("/api/ingest/telemetry", status_code=202)
@rate_limit_write(limit="1000/minute")
async def ingest_telemetry(
    payload: TelemetryBatch,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id),
):
    """
    Accepts batched sensor readings from edge gateways.
    Writes to InfluxDB cloud bucket.
    Triggers real-time alert evaluation.
    """
```

**Request body:**
```json
{
  "plant_id": "uuid",
  "batch": [
    {
      "ts":        "2026-07-20T14:32:01.123Z",
      "sensor_id": "CO2-GAS-01",
      "value":     14.72,
      "unit":      "vol%",
      "quality":   "GOOD",
      "raw_counts": 17841,
      "cal_offset": -0.12,
      "cal_slope":  1.003
    }
    // ... up to 500 items
  ]
}
```

### 4.2 Alert Evaluation Pipeline

On receipt of each batch, the API triggers an async alert scan:

```python
async def evaluate_alerts(readings: list[TelemetryPoint], plant_id: UUID, db: AsyncSession):
    """
    Runs after telemetry is written to InfluxDB.
    Checks:
      1. Sensor quality != GOOD for critical sensors → quality alert
      2. Process value crosses configured threshold → process alarm
      3. Sensor offline (no data for > 2× max_latency) → comms alarm
    Persists AlarmRecord to PostgreSQL.
    Publishes to WebSocket channel: cbms/plants/{id}/alarms
    """
```

### 4.3 Device Authentication

Raspberry Pi gateways authenticate with rotating 24-hour device tokens:

```
POST /api/auth/device
Body: { "device_id": "pi-plant-001", "device_secret": "...(HMAC-SHA256 of timestamp)..." }
Response: { "access_token": "eyJ...", "expires_in": 86400 }
```

Device secrets are provisioned at factory setup and stored in `/etc/cbms-gateway/.env` (mode 600, owner cbms).

---

## 5. Real-Time WebSocket Feed

The edge data flows to the Digital Twin view via the existing WebSocket architecture:

```
Topic: cbms/plants/{plant_id}/telemetry
Message type: SENSOR_UPDATE
Payload: { sensor_id, tag, value, unit, quality, ts }
```

The `digital-twin/` frontend subscribes to this topic and renders live sensor readings on the P&ID overlay. Sensor quality codes are mapped to indicator colours:

| Quality | Colour | Icon |
|---|---|---|
| `GOOD` | 🟢 Green | ● |
| `UNCERTAIN` / `CAL_REQUIRED` | 🟡 Amber | ◐ |
| `BAD_*` | 🔴 Red | ✕ |

---

## 6. Deployment

### 6.1 Edge Gateway — First Boot Provisioning

```bash
# Run on Pi after flashing OS image:
curl -sSL https://setup.cbms.app/install-gateway | bash
# Prompts for: plant_id, api_key, serial port assignments
```

### 6.2 OTA Update Strategy

Edge gateway software updates use a dual-partition A/B scheme:
- **Active partition** runs the current gateway binary
- **Inactive partition** receives the new OTA update
- After 5-minute canary window with no watchdog trips, new partition becomes active
- Rollback is automatic if watchdog fires within the canary window

```
Deployment flow:
  CBMS Cloud → MQTT: cbms/devices/{id}/ota/announce
  Pi gateway: downloads signed tarball from CDN
  Pi gateway: writes to inactive partition
  Pi gateway: reboots into new partition
  Pi gateway: reports health → CBMS Cloud: confirms success
```

### 6.3 Monitoring (Prometheus metrics from gateway)

The gateway exports metrics at `http://localhost:9100/metrics`:

```
cbms_sensor_readings_total{sensor_id, quality}  counter
cbms_sensor_value{sensor_id}                    gauge (latest reading)
cbms_cloud_sync_lag_seconds                     gauge
cbms_cloud_sync_batch_size                      histogram
cbms_local_buffer_rows                          gauge
cbms_modbus_errors_total{sensor_id}             counter
cbms_serial_errors_total{sensor_id}             counter
```

Scraped by Prometheus at each site; federated to cloud Prometheus for multi-plant dashboards.

---

## 7. Data Rate Budget

| Group | Sensors | Rate | Payload/message | Data rate |
|---|---|---|---|---|
| Fast (10 Hz) | 3 sensors | 10 Hz | ~200 bytes | ~6 KB/s |
| Medium (1 Hz) | 8 sensors | 1 Hz | ~200 bytes | ~1.6 KB/s |
| Slow (0.1 Hz) | 7 sensors | 0.1 Hz | ~200 bytes | ~140 B/s |
| **Total** | 18 sensors | — | — | **~8 KB/s** |

4G LTE at 5 Mbps upload → **0.002% utilisation**. Budget headroom is enormous; even 100 plants on one 4G SIM would be < 1 Mbps.

---

## 8. Open Items

| Item | Priority | Owner |
|---|---|---|
| Implement `cbms-gateway` Python package + systemd unit | 🔴 High | Platform Eng |
| Write `POST /api/ingest/telemetry` endpoint | 🔴 High | Platform Eng |
| Wire telemetry into InfluxDB cloud bucket | 🔴 High | Platform Eng |
| Implement device JWT auth (`/api/auth/device`) | 🔴 High | Security |
| WebSocket `SENSOR_UPDATE` message type in Digital Twin | 🟡 Medium | Frontend |
| OTA update mechanism (A/B partition) | 🟡 Medium | DevOps |
| Prometheus exporter for gateway metrics | 🟡 Medium | DevOps |
| Integration test: gateway → API → InfluxDB round-trip | 🟡 Medium | QA |
| First-boot provisioning script | 🟢 Low | Platform Eng |
