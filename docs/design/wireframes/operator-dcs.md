# Operator DCS — Wireframes

**Route prefix**: `/operator/*`  
**Audience**: Plant operators, shift engineers  
**Device**: 24″ industrial monitor · 10″ tablet (touch-optimized)

---

## Page: Live Ops (`/operator/live`)

### Above the fold — 0 scroll

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER (48 px, always visible)                                   │
│  🌿 CarbonLattice  │ Live Ops  │ Plants ▾  │ Alarms  │ Settings │
│                                            🔔2  🟢 Live • 2 ms  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ALERT BANNER (only when alerts present — highest visual priority)│
│  ⚠ 2 ALERTS  •  1 CRITICAL: "SO₂ outlet 215 mg/Nm³"  [VIEW ▸]  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ KPI STRIP (6 tiles, full width, ~72 px tall)                     │
│  [CO₂: 87.2% ✅] [SO₂: 96.5% ✅] [T: 40.2°C ✅]               │
│  [ΔP: 220 ⚠]    [pH: 8.5 ✅]   [Flow: 10k ✅]                  │
│                    ↑ click any tile → sensor detail drill-down   │
└──────────────────────────────────────────────────────────────────┘

┌────────────────────────────┐  ┌───────────────────────────────┐
│ PLANT SCHEMATIC (60%)       │  │ ALARM LIST (40%)              │
│                             │  │                               │
│  [SVG live sensor overlay]  │  │  ● CRITICAL  SO₂ 215 mg/Nm³  │
│  Each tag shows live value  │  │    [Acknowledge]  [Escalate]  │
│  Colour = alarm state       │  │                               │
│  Click tag → sensor detail  │  │  ● WARNING   Mesh ΔP high    │
│                             │  │    [Acknowledge]              │
│  [BLOWER]  [PUMP A]         │  │                               │
│  [PUMP B]  [TOWER]          │  │  ● INFO      Maint due 48 h   │
│                             │  │    [Acknowledge]              │
└────────────────────────────┘  └───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ACTUATOR DRAWER (collapsible, pull-up from bottom — ~80 px)      │
│  [▶ ID Fan] [⏸ Pump A] [▶ Pump B] [▶ Tower] [▶ Ultrasonic]     │
│  ↑ Each button = toggle with confirmation dialog                 │
└──────────────────────────────────────────────────────────────────┘
```

### Interaction rules

| Action | Behavior |
|---|---|
| Click KPI tile | Opens `<SensorDetail>` panel (right slide-in) |
| Click actuator | Shows `<ConfirmDialog>` ("Start Pump A?") |
| Confirm actuate | Sends command · shows success toast |
| Click alert | Expands row with recommended action |
| Click Acknowledge | Marks alert acknowledged · audit log entry |
| Click Escalate | Opens escalation modal (PagerDuty / on-call) |
| Click VIEW in banner | Scrolls to alarm list |

---

## Page: Plant Schematic (`/operator/schematic/:plantId`)

```
┌──────────────────────────────────────────────────────────────────┐
│ Full-width SVG schematic of the CBMS plant                       │
│                                                                  │
│   [INLET DUCT]──▶[PRE-SCRUBBER]──▶[REACTOR TOWER]              │
│        │                │                  │                     │
│  [14.0% CO₂]      [pH: 8.5]         [40.2°C]                   │
│  [1200 mg SO₂]   [8.5 L/G ratio]    [Mesh ΔP: 220]             │
│                                             │                    │
│                                    [OUTLET DUCT]                 │
│                                    [1.8% CO₂ ✅]                │
│                                    [38 mg SO₂ ✅]               │
│                                                                  │
│  Each sensor tag:  [label  value  ●status] ← clickable          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Page: Alarm History (`/operator/alarms`)

```
┌──────────────────────────────────────────────────────────────────┐
│ Filters: [Today ▾]  [All Severities ▾]  [All Plants ▾]  [Search]│
├──────────────┬────────────┬──────────────────────┬──────────────┤
│ Time         │ Severity   │ Message              │ Resolved by  │
├──────────────┼────────────┼──────────────────────┼──────────────┤
│ 10:32:15     │ CRITICAL   │ SO₂ outlet 215 mg/Nm³│ Operator B   │
│ 09:15:02     │ WARNING    │ Mesh ΔP 235 mmH₂O    │ Auto-cleared │
│ 08:45:11     │ INFO       │ Maint due in 48 h    │ Acknowledged │
└──────────────┴────────────┴──────────────────────┴──────────────┘
│ [Export CSV]                                          [← Back]   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Page: Shift Handover (`/operator/handover`)

```
┌──────────────────────────────────────────────────────────────────┐
│  Shift Handover — 2026-07-12 Day Shift                           │
├──────────────────────────────────────────────────────────────────┤
│  Outgoing operator:  [Operator Name ___________]                 │
│  Incoming operator:  [Operator Name ___________]                 │
├──────────────────────────────────────────────────────────────────┤
│  Auto-generated summary:                                         │
│  • CO₂ capture avg: 87.2% (target: 85%) ✅                       │
│  • 2 alerts raised, 2 acknowledged                               │
│  • Pump A stopped at 09:32, restarted at 09:48                   │
├──────────────────────────────────────────────────────────────────┤
│  Operator notes:                                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ [Free text — max 1000 chars]                              │  │
│  └────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  [Sign Off & Submit]                          [Save Draft]       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Accessibility & Touch Guidelines

- Minimum touch target: **44 px × 44 px**
- Minimum font size: **16 px** (body), **20 px** (KPI values)
- High contrast: all text ≥ 7:1 ratio on dark background
- Bottom navigation bar on tablet (thumb-reachable)
- All actions keyboard-accessible (Tab, Enter, Esc)
- Screen reader: all status indicators have `role="status"` and `aria-label`
