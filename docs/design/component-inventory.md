# Component Inventory

## Operator DCS Components

| Component | File | Props | Purpose | Priority |
|---|---|---|---|---|
| `<AlertBanner>` | `features/operator/components/AlertBanner.tsx` | `alerts: AlertData[]`, `onView: () => void` | Sticky top bar when alerts present | 🔴 Critical |
| `<KPIStrip>` | `features/operator/components/KPIStrip.tsx` | `state: TwinState`, `onTileClick` | 6-tile live KPI row | 🔴 Critical |
| `<PlantSchematic>` | `features/operator/components/PlantSchematic.tsx` | `state: TwinState` | Live SVG overlay with sensor tags | 🟠 High |
| `<AlarmList>` | `features/operator/components/AlarmList.tsx` | `alerts: Map<id, AlertData>`, `onAck`, `onEscalate` | Severity-sorted side panel | 🔴 Critical |
| `<ActuatorDrawer>` | `features/operator/components/ActuatorDrawer.tsx` | `state: TwinState`, `onCommand`, `canControl` | Pull-up bottom drawer with toggles | 🔴 Critical |
| `<ConfirmDialog>` | `features/operator/components/ConfirmDialog.tsx` | `title`, `message`, `onConfirm`, `onCancel` | Safety confirmation before actuation | 🔴 Critical |
| `<SensorDetail>` | `features/operator/components/SensorDetail.tsx` | `metric: string`, `history`, `onClose` | Single-metric drill-down panel | 🟠 High |
| `<OperatorNav>` | `features/operator/components/OperatorNav.tsx` | `plantId`, `alertCount` | 4-item top nav + notification bell | 🔴 Critical |
| `<ShiftHandover>` | `features/operator/pages/ShiftHandover.tsx` | — | End-of-shift notes form | 🟡 Medium |
| `<AlarmHistory>` | `features/operator/pages/AlarmHistory.tsx` | — | Paginated alarm audit log | 🟡 Medium |
| `<OperatorDashboard>` | `features/operator/pages/OperatorDashboard.tsx` | `plantId` | Page container | 🔴 Critical |

---

## Executive / Report Components

| Component | File | Props | Purpose | Priority |
|---|---|---|---|---|
| `<PortfolioKPIs>` | `features/executive/components/PortfolioKPIs.tsx` | `data: PortfolioSummary` | 6 hero KPI cards with trend arrows | 🔴 Critical |
| `<PlantTable>` | `features/executive/components/PlantTable.tsx` | `plants: PlantRow[]`, `onRowClick` | Sortable, filterable, exportable table | 🔴 Critical |
| `<TrendChart>` | `features/executive/components/TrendChart.tsx` | `series`, `dateRange`, `metric` | Multi-line Recharts chart | 🟠 High |
| `<AutoInsights>` | `features/executive/components/AutoInsights.tsx` | `insights: Insight[]` | AI-generated anomaly cards | 🟠 High |
| `<GlobalFilters>` | `features/executive/components/GlobalFilters.tsx` | `value`, `onChange` | Period / Region / Plant filter bar | 🟠 High |
| `<ActionBar>` | `features/executive/components/ActionBar.tsx` | `onReport`, `onExport` | Export + generate buttons | 🟡 Medium |
| `<ReportBuilder>` | `features/executive/pages/ReportBuilder.tsx` | — | PDF generation form | 🟡 Medium |
| `<PlantDetail>` | `features/executive/pages/PlantDetail.tsx` | `plantId` | Single plant deep-dive | 🟠 High |
| `<ExecutiveDashboard>` | `features/executive/pages/ExecutiveDashboard.tsx` | — | Portfolio page container | 🔴 Critical |
| `<ExecNav>` | `features/executive/components/ExecNav.tsx` | — | 5-item top nav | 🔴 Critical |

---

## Shared Components (both views)

| Component | File | Purpose |
|---|---|---|
| `<ConnectionStatus>` | `features/digital-twin/components/ConnectionStatus.tsx` | WS health (already built Task 4.1) |
| `<OperatingModeIndicator>` | `features/digital-twin/components/OperatingModeIndicator.tsx` | Mode pill (already built Task 4.1) |
| `<AlertPanel>` | `features/digital-twin/components/AlertPanel.tsx` | Alert list (already built Task 4.1) |

---

## Component Design Constraints

### Operator DCS
- Minimum touch target: **44 px × 44 px**
- All KPI values: `font-size: 20px` minimum
- Color contrast: **≥ 7:1** on dark background (WCAG AAA)
- No modals that obscure the whole screen (use slide-in panels)
- Every destructive action has a confirmation step

### Executive
- Minimum interactive target: **32 px × 32 px**
- All chart tooltips keyboard-accessible
- Export buttons always visible (not buried in menus)
- Data tables have `aria-sort` on sortable columns
- Color never the only signal (always +icon or +text)
