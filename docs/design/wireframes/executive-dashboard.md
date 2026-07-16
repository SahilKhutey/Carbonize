# Executive Dashboard — Wireframes

**Route prefix**: `/executive/*`  
**Audience**: Plant managers · Investors · C-suite  
**Device**: 27″ desktop (mouse-optimized); graceful degradation on tablet

---

## Page: Portfolio Dashboard (`/executive/dashboard`)

### Above the fold

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                           │
│  🌿 CarbonLattice  Dashboard  Plants  Reports  Analytics  [User] │
└──────────────────────────────────────────────────────────────────┘

┌──── GLOBAL FILTERS (persistent) ─────────────────────────────────┐
│  Period: [Last 90 days ▾]   Region: [All ▾]   Plant: [All ▾]    │
└──────────────────────────────────────────────────────────────────┘

┌──── HERO KPIs (portfolio-wide, vs. prior period) ─────────────────┐
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Total CO₂ Captured│  │  CCTS Credits    │  │  Cost Savings    │ │
│  │  2,847 tonnes    │  │  ₹52,00,000      │  │  ₹18.2 Crore     │ │
│  │  ▲ +12% vs Q2   │  │  ▲ +8% vs Q2    │  │  ▲ +24% vs Q2   │ │
│  │  (Month-to-Date) │  │  (Year-to-Date)  │  │  (Year-to-Date)  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Active Plants    │  │  Avg Capture %   │  │  CO₂ tCO₂/MWh   │ │
│  │  23 active       │  │  85.4%           │  │  0.42            │ │
│  │  1 fault         │  │  ▲ +2.1 pp      │  │  ▼ -0.03 (good) │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Below the fold

```
┌──── PLANT TABLE ──────────────────────────────────────────────────┐
│ [Sort by ▾] [Filter ▾]              [Export CSV]  [Export Excel]  │
├────────┬──────────┬───────────┬──────────┬──────────┬────────────┤
│ Plant  │ Status   │ CO₂ Capt  │ NPV/yr   │ CCTS     │ Last Maint │
├────────┼──────────┼───────────┼──────────┼──────────┼────────────┤
│ Plant A│ 🟢 OK   │ 87.2%     │ ₹4.2 Cr  │ 450 ton  │ 12 days   │
│ Plant B│ 🟡 Warn  │ 78.3%     │ ₹3.8 Cr  │ 420 ton  │ 45 days   │
│ Plant C│ 🟢 OK   │ 91.5%     │ ₹5.1 Cr  │ 520 ton  │ 8 days    │
│ Plant D│ 🔴 Fault │ 52.1%     │ ₹1.2 Cr  │ 210 ton  │ 72 days   │
│ ...    │          │           │          │          │            │
└────────┴──────────┴───────────┴──────────┴──────────┴────────────┘

┌──── PORTFOLIO TREND CHART ────────────────────────────────────────┐
│  [Metric: CO₂ Capture % ▾]  [All Plants ▾]  [Jan–Jul 2026 ▾]     │
│                                                                   │
│  100%┤                                              ╱─────────   │
│      │                               ╱─────────────             │
│   85%┤                  ╱───────────                            │
│      │       ╱─────────                                          │
│   70%┤ ──────                                                    │
│      └──────────────────────────────────────────────────────── │
│        Jan    Feb    Mar    Apr    May    Jun    Jul             │
│                                                           [PNG]  │
└──────────────────────────────────────────────────────────────────┘

┌──── AUTO-GENERATED INSIGHTS ──────────────────────────────────────┐
│  💡 Plant B CO₂ capture fell 8% in week 14 (Apr 1–7)            │
│     Possible causes: enzyme concentration drift, sensor recalib  │
│     [Drill Down →]                                               │
│                                                                  │
│  💡 Plant C NPV on track to exceed projection by 14%            │
│     Based on current capture rate and CCTS spot price           │
│     [View Report →]                                              │
└──────────────────────────────────────────────────────────────────┘

┌──── ACTION BAR ────────────────────────────────────────────────┐
│  [📄 Generate Board Report]  [📊 Export Data]  [⚙️ Alerts]      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Page: Plant Detail (`/executive/plants/:plantId`)

```
┌──── BREADCRUMB ───────────────────────────────────────────────────┐
│  Dashboard > Plants > Plant B                                     │
└──────────────────────────────────────────────────────────────────┘

┌──── PLANT KPI HEADER ─────────────────────────────────────────────┐
│  Plant B — Nashik, Maharashtra              Status: 🟡 Warning    │
│  Last updated: 5 minutes ago                                      │
│                                                                   │
│  [CO₂: 78.3%] [SO₂: 94.1%] [NPV: ₹3.8 Cr/yr] [CCTS: 420 ton]  │
└──────────────────────────────────────────────────────────────────┘

┌──── TREND CHARTS ──────────────────────────────────────────────────┐
│  [Tabs: CO₂ Capture | SO₂ Capture | NPV | Maintenance cost]       │
│                                                                   │
│  ─── CO₂ Capture % — Last 90 Days ───────────────────────────    │
│  90%┤                    ╱──────────                             │
│     │        ╱──────────                                          │
│  80%┤ ──────            ╲──────   ←── Week 14 anomaly            │
│     │                         ╲──                                 │
│  70%┤                               [Annotation: enzyme re-dosed] │
│     └───────────────────────────────────────────────────────────  │
│      Week 1     Week 4     Week 7     Week 10    Week 13         │
└──────────────────────────────────────────────────────────────────┘

┌──── REPORT ACTIONS ───────────────────────────────────────────────┐
│  [📄 Generate Plant Report]  [📊 Export CSV]  [📧 Send to Email]  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Page: Report Builder (`/executive/reports`)

```
┌──────────────────────────────────────────────────────────────────┐
│  Generate Report                                                 │
│                                                                  │
│  Report type:  [● Board Pack  ○ Monthly Summary  ○ CPCB Report] │
│  Plants:       [All ▾ / Select multiple]                        │
│  Period:       [Q2 2026 (Apr–Jun) ▾]                            │
│  Sections:     [☑ KPIs  ☑ Trends  ☑ Maintenance  ☑ CCTS]       │
│  Branding:     [Company logo upload]                             │
│                                                                  │
│  Preview:                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  [PDF Preview pane — 2 pages thumbnail]                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [Generate PDF]  [Send by Email]  [Schedule Monthly]            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Interaction Rules

| Action | Behavior |
|---|---|
| Click portfolio KPI | Drills into portfolio-wide trend for that metric |
| Click plant row | Navigates to Plant Detail page |
| Click sort column | Sorts table (asc/desc toggle) |
| Click filter | Opens filter panel (multi-select) |
| Click Export CSV | Downloads plant-list.csv |
| Click trend chart | Opens full-screen chart modal |
| Click insight "Drill Down" | Navigates to Plant Detail with date range pre-set |
| Click Generate Board Report | Opens Report Builder with plant pre-selected |

---

## Accessibility

- All interactive table columns have `scope="col"` and sort `aria-sort` attribute
- Charts have `role="img"` with descriptive `aria-label`
- All percentage trends have a text alternative (e.g., "Up 12 percent vs prior period")
- PDF export is machine-readable (tagged PDF)
- Color is never the only signal (always paired with icon or text)
