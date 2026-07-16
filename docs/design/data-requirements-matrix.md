# Data Requirements Matrix

## Legend
- ✅ Primary consumer (always shown)
- 🟡 Optional (configurable, or secondary)
- ❌ Not shown (wrong context)

---

## Real-Time Sensor Data (via WebSocket, 1 Hz)

| Data Point | Operator DCS | Executive | Update | Source |
|---|---|---|---|---|
| CO₂ outlet % | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| SO₂ outlet mg/Nm³ | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| Mesh ΔP mmH₂O | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| Reactor temp °C | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| pH | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| Gas flow Nm³/hr | ✅ KPI strip | ❌ | 1 s | WebSocket tick |
| Operating mode | ✅ mode pill | 🟡 fault count | 1 s | WebSocket tick |
| Active alarms | ✅ full list | ❌ (count only) | Event | WebSocket event |
| Actuator status | ✅ actuator drawer | ❌ | 1 s | WebSocket tick |
| CO₂ capture % | ✅ live | ❌ | 1 s | WebSocket tick |
| SO₂ capture % | ✅ live | ❌ | 1 s | WebSocket tick |

---

## Aggregated / Historical Data (REST API, lazy-loaded)

| Data Point | Operator DCS | Executive | Refresh | Source |
|---|---|---|---|---|
| Today CO₂ total (tonnes) | 🟡 optional | ✅ hero KPI | 1 hr | `GET /api/analytics/summary` |
| 30-day capture efficiency | 🟡 optional | ✅ trend chart | 1 day | `GET /api/analytics/trends` |
| Cumulative CCTS credits | ❌ | ✅ hero KPI | 1 day | `GET /api/analytics/ccts` |
| NPV per year | 🟡 per-plant | ✅ plant table | 1 day | `GET /api/analytics/npv` |
| Portfolio NPV | ❌ | ✅ hero KPI | 1 day | `GET /api/analytics/portfolio` |
| Maintenance schedule | ✅ (live alert) | ✅ (calendar) | Event | `GET /api/maintenance` |
| CPCB compliance report | ❌ | ✅ reports section | 1 month | `GET /api/reports/cpcb` |
| Industry benchmark | ❌ | ✅ analytics | 1 day | `GET /api/analytics/benchmark` |
| Trend: 90-day capture | ❌ | ✅ plant detail | On demand | `GET /api/analytics/trends` |
| Anomaly annotations | ❌ | ✅ insights panel | 1 hr | `GET /api/analytics/insights` |
| Cost savings vs baseline | ❌ | ✅ hero KPI | 1 day | `GET /api/analytics/savings` |

---

## API Endpoint Summary

```
# Operator (real-time)
WS /api/v1/twin/{plantId}/stream    ← all live sensor data (Task 3.5)

# Executive (aggregated)
GET /api/analytics/portfolio         ← portfolio-wide KPIs
GET /api/analytics/summary?plant=X  ← per-plant daily summary
GET /api/analytics/trends?plant=X&metric=co2_capture&days=90
GET /api/analytics/ccts?org=Y       ← cumulative CCTS
GET /api/analytics/npv?org=Y        ← NPV by plant
GET /api/analytics/insights         ← AI-generated anomaly list
GET /api/analytics/savings          ← cost savings
GET /api/analytics/benchmark        ← industry comparison
GET /api/maintenance?plant=X        ← maintenance schedule
GET /api/reports/cpcb?plant=X&month=YYYY-MM  ← CPCB report
```

---

## Update Cadence

```typescript
// Operator: aggressive (must never be stale)
const OPERATOR_WS_TICK_INTERVAL_S = 1;

// Executive: lazy (performance + cost)
const EXECUTIVE_POLL_INTERVAL_MS  = 60_000;   // 1 minute
const EXECUTIVE_CACHE_TTL_S       = 300;       // 5 minute client-side cache
```

---

## Rule of Thumb

> **Operator** wants *current* data (within 2 seconds).  
> **Executive** wants *historical and comparative* data (within the last business day).  
>
> They share the same database, but consume different aggregations.
