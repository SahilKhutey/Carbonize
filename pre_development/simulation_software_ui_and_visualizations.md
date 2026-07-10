# 📊 Simulation Software: Dashboards, UI Components, Communications & Visualizations

This document provides a comprehensive technical reference for the frontend components, design systems, real-time charts, and WebSocket communication patterns in the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. UI Architecture & Hierarchy

The frontend is a React 19 single-page application structured inside the `packages/web/` workspace.

```
App
├── Providers (QueryClientProvider, RouterProvider, AuthProvider)
└── AppShell
    ├── Sidebar (Tenant Org Switcher, Navigation Links)
    ├── Header (Breadcrumbs, System Telemetry, Notifications)
    └── Page Outlet
        ├── Dashboard (Recent simulations, CPCB compliance gauges)
        ├── Simulation Detail (Live WebSockets progress, ResultsTabs)
        └── Digital Twin (High-frequency sensor graphs, actuator panel)
```

---

## 2. Design System tokens

Predefined CSS tokens are bound inside Tailwind and [tokens.ts](file:///c:/Users/ASUS/Documents/Carbonize/packages/web/src/styles/tokens.ts) to enforce visual consistency:

*   **Primary Brand:** Emerald Green (`#10b981`) represents biomimetic mineralization.
*   **Neutral Gray:** Gray slate scales (`#111827` to `#f9fafb`) for Sleek Dark Mode compatibility.
*   **Typography Display:**Outfit and Inter fonts mapped via Google Fonts for sleek premium display styles.
*   **Capture Metrics Color Code:**
    *   $\text{Capture } > 80\%$: Emerald Green.
    *   $\text{Capture } 50\% - 80\%$: Warning Orange.
    *   $\text{Capture } < 50\%$: Danger Red.

---

## 3. Component Catalog

### 3.1 Button Systems (`packages/web/src/components/ui/Button.tsx`)
Exposes custom style variants via class-variance-authority (`cva`):
*   `primary`: Background brand green, white text, shadow-sm (Run Simulation, Save Formulation).
*   `secondary`: Outline gray border, black text, white background (Cancel, Go Back).
*   `destructive`: Dark red background, white text (Delete profile, Revoke credentials).
*   `success`: Emerald green background (Submit BEE compliance claim).

### 3.2 WebSocket Live Progress Tracker (`LiveProgressTracker.tsx`)
Renders a reactive horizontal progress bar subscribed to WebSocket stream events.
*   **WebSockets Channel:** `ws://<api>/api/v1/simulations/{runId}/stream`
*   **Event Handling:** Listens to JSON events containing `pct` (percentage progress) and `stage` (e.g., `kinetics`, `monte_carlo`). Updates the stage timeline state variables in real time.

### 3.3 Real-Time Sensor Charting (`RealtimeTimeSeries.tsx`)
Plots live sensor data from the digital twin columns using **Recharts**:
*   **Auto-Polling:** Queries sensor values (transient pH, column gas flux, temperature) via Axios every 1,000ms.
*   **Reference Indicators:** Draws dashed reference lines mapping critical warning and danger limits (e.g. pH danger line at $< 7.0$).

---

## 4. Communication Protocols & WebSockets

The client communicates with the FastAPI back-end using three primary integration paths:

1.  **JSON REST API:** Plant CRUD actions, auth checks, and simulation task submissions.
2.  **WebSocket Streams:** Broadcasts Celery pipeline status logs (`simulations:{id}:progress`) to client UI in real time.
3.  **Presigned URLs:** Pulls PDF reports from S3 buckets with temporary 15-minute access tokens.
