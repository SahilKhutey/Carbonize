# IA Decisions — Rationale

Six key architectural decisions with explicit rationale for this platform.

---

## Decision 1: Two Separate Route Trees, Two Separate App Shells

**What**: `/operator/*` and `/executive/*` are fully separate feature trees with separate navigation, color palettes, and component sets.

**Why not one shell with two "modes"?**

| Concern | Why separate shells win |
|---|---|
| Navigation | Operator: 4 items (terse). Executive: 8 items (rich) |
| Color palette | Operator: industrial dark (SCADA). Executive: corporate light |
| Data density | Operator: dense, every pixel counts. Executive: spacious, scannable |
| Interaction | Operator: large buttons + confirmations. Executive: filters + drill-down |
| Update pattern | Operator: WebSocket (1 Hz). Executive: REST poll (60 s) |
| Mental model | "Is it safe?" vs "Is it worth it?" |

A single shell with two modes creates:
- Confusing nav for both users
- Stale real-time data leaking into executive view
- Touch targets too small for operators
- Performance overhead (WS open even on exec view)

---

## Decision 2: Role-Based Default Route on Login

**What**: `getDefaultRoute(role)` returns `/operator/live` for operators/engineers and `/executive/dashboard` for everyone else.

**Why**: Users should land on the page they use 95% of the time. Cognitive overhead of choosing a view every login compounds across hundreds of daily logins.

**Implementation**:
```typescript
export type UserRole = "operator" | "engineer" | "admin" | "manager" | "investor" | "viewer";

export function getDefaultRoute(role: UserRole): string {
  switch (role) {
    case "operator":
    case "engineer":
      return "/operator/live";
    default:
      return "/executive/dashboard";
  }
}
```

---

## Decision 3: No "DCS Lite" for Executives

**What**: Executives do NOT get a simplified real-time view.

**Why**: Real-time data without operational context is dangerous and misleading.
- A 3% CO₂ spike might alarm an investor, but the operator knows it's a planned enzyme reload
- Executives misinterpreting real-time data causes unnecessary escalations
- Real-time data is cognitively overwhelming without the operational mental model

**Instead**: Executives get daily/weekly aggregates with trend context and anomaly annotations. If they need real-time, they speak to the operator (correct separation of concerns).

---

## Decision 4: Color Semantics Differ Between Views

**The problem**: Red means different things to different people.

| Color | Operator DCS | Executive View |
|---|---|---|
| 🔴 Red | **CRITICAL ALARM — act now** | Underperforming vs target (informational) |
| 🟡 Amber | **WARNING — monitor closely** | Below target — watch trend |
| 🟢 Green | Normal — continue | On track |
| 🔵 Blue | Informational | Informational |

**Why this matters**: If an executive sees red and thinks "act now", they'll call the control room unnecessarily. If an operator sees a calm executive-style "below target" yellow, they may not respond fast enough to an actual alarm.

**Implementation**: Two separate CSS token sets.
```css
/* Operator: high-signal alarm colors */
--alarm-critical: theme('colors.red.500');    /* act now */
--alarm-warning:  theme('colors.amber.400');  /* monitor */
--alarm-normal:   theme('colors.emerald.500');/* continue */

/* Executive: calm BI status colors */
--status-bad:     theme('colors.red.400');    /* inform */
--status-warn:    theme('colors.yellow.400'); /* trend */
--status-good:    theme('colors.green.400');  /* on track */
```

---

## Decision 5: Different Update Cadences

**What**: Operator view consumes WebSocket at 1 Hz. Executive view polls REST at 60 s.

**Why different cadences?**
- Operator: A 2-second stale KPI could mean missing a critical alarm crossing
- Executive: A 60-second stale portfolio KPI is perfectly acceptable; they're reviewing trends not instants
- Performance: Keeping a WS connection open on the executive view wastes server resources and battery

**Implementation**:
```typescript
// In useTwinStream (operator):
const tickIntervalSeconds = 1;

// In usePortfolioData (executive):
const POLL_INTERVAL_MS = 60_000;
const staleTime = 5 * 60 * 1000; // 5-minute React Query cache
```

---

## Decision 6: Operator View is Touch-First; Executive is Mouse-First

**What**: Two separate sets of responsive breakpoints and interaction targets.

**Operator touch targets**:
- Minimum: 44 px × 44 px (WCAG 2.5.5 AAA)
- Preferred: 56 px × 56 px for actuator buttons
- Bottom navigation bar on mobile/tablet (thumb-reachable)
- Swipe gestures for common actions

**Executive mouse targets**:
- Minimum: 24 px × 24 px (WCAG 2.5.5 AA)
- Top navigation (standard desktop pattern)
- Hover tooltips on chart data points
- No swipe gestures

**Why the operator view must be touch-friendly**: Operators in the field use ruggedized tablets. They may be wearing gloves. The screen may be in sunlight (high contrast needed). Precise mouse clicks are not possible.
