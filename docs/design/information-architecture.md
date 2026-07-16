# Information Architecture — CBMS Digital Twin Platform

## Overview

The CBMS platform serves **two radically different users** with two separate products sharing the same backend.

---

## 1. User Archetypes

| Dimension | Operator DCS | Executive / Report |
|---|---|---|
| **User** | Plant operator (control room) | Plant manager · Investor · Executive |
| **Context** | Standing, high-stress, 24/7 | Sitting, reviewing, periodic |
| **Time horizon** | Now (next 5 minutes) | History (last quarter) + forecast |
| **Decision type** | Operational — "press the button" | Strategic — "approve the investment" |
| **Update frequency** | Real-time (1 Hz) | Daily / Weekly |
| **Data density** | Dense, signal-rich | Compressed, insight-focused |
| **Aesthetic** | Industrial SCADA / DCS | Polished BI dashboard |
| **Failure mode** | Missed alarm → plant shutdown | Missed insight → bad investment |
| **Color semantics** | Alarm colors (red=act now) | Status colors (red=inform) |
| **Interaction** | Push buttons · confirmations | Drill-down · filters · exports |
| **Device** | 24″ industrial monitor / 10″ tablet | 27″ desktop (mouse) |
| **Failure tolerance** | Zero — must not miss critical events | High — delays acceptable |

> **Critical insight**: These are NOT two modes of the same view. They are fundamentally different products.

---

## 2. Route Architecture

```
/operator/live              →  OperatorDashboard   (DCS-style, real-time)
/operator/schematic/:plantId→  PlantSchematic      (visual sensor layout)
/operator/alarms            →  AlarmHistory        (last 24 h audit log)
/operator/handover          →  ShiftHandover       (end-of-shift notes)

/executive/dashboard        →  ExecutiveDashboard  (portfolio overview)
/executive/plants           →  PlantTable          (all plants, filterable)
/executive/plants/:plantId  →  PlantDetail         (single-plant deep-dive)
/executive/reports          →  ReportBuilder       (PDF report generation)
/executive/analytics        →  Analytics           (advanced trend analysis)

/twin/:plantId              →  TwinPage            (live digital twin, Task 4.1)
```

---

## 3. Role-Based Default Route

```typescript
function getDefaultRoute(role: UserRole): string {
  if (role === "operator")  return "/operator/live";
  if (role === "engineer")  return "/operator/live";   // engineers get same view
  return "/executive/dashboard";                        // admin, manager, investor
}
```

---

## 4. Key IA Decisions

See [IA-decisions-rationale.md](./IA-decisions-rationale.md) for full rationale.

| Decision | Summary |
|---|---|
| Two separate route trees | Different nav, palette, density, and update pattern |
| Role-based default route | Operators land on live ops; execs land on portfolio |
| No "DCS Lite" for execs | Execs see BI truth, not real-time stream |
| Color semantics differ | Operator red = act now; Exec red = inform |
| Different refresh rates | Operator 1 s; Exec 60 s |
| Operator is touch-first | 44 px targets, bottom nav, high contrast |

---

## 5. Navigation

### Operator
```
[Live Ops]  [Plants ▾]  [Alarms]  [Settings]      [User]  [🔴2]
```

### Executive
```
[LOGO]  Dashboard  Plants  Reports  Analytics      [User]
```

---

## 6. Screen Inventory

### Operator DCS

| Screen | Route | Critical Path |
|---|---|---|
| Live Ops (default) | `/operator/live` | ✅ YES |
| Plant Schematic | `/operator/schematic/:id` | ✅ YES |
| Actuator Drawer | (embedded in Live Ops) | ✅ YES |
| Alert List | (embedded in Live Ops) | ✅ YES |
| Sensor Detail | (modal / panel) | 🟠 NO |
| Alarm History | `/operator/alarms` | 🟠 NO |
| Shift Handover | `/operator/handover` | 🟠 NO |
| Settings | `/operator/settings` | 🟢 NO |

### Executive / Report

| Screen | Route | Critical Path |
|---|---|---|
| Dashboard (default) | `/executive/dashboard` | ✅ YES |
| Plant Table | `/executive/plants` | ✅ YES |
| Plant Detail | `/executive/plants/:id` | 🟠 NO |
| Trend Charts | (embedded in Plant Detail) | 🟠 NO |
| Report Builder | `/executive/reports` | 🟠 NO |
| Analytics | `/executive/analytics` | 🟢 NO |
| Alerts Config | `/executive/alerts` | 🟢 NO |
