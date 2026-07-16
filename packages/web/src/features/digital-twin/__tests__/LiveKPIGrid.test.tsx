/**
 * packages/web/src/features/digital-twin/__tests__/LiveKPIGrid.test.tsx
 */

import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LiveKPIGrid } from "../components/LiveKPIGrid";
import { TwinState } from "../types/twin";

// ---------------------------------------------------------------------------
// Fixture
// ---------------------------------------------------------------------------

const base: TwinState = {
  plant_id:         "plant-abc",
  org_id:           "org-xyz",
  operating_mode:   "running",
  current_actuals: {
    co2_inlet_pct:      14.0,
    co2_outlet_pct:     1.8,
    so2_inlet_mg_nm3:   1200,
    so2_outlet_mg_nm3:  38,
    mesh_dp_mmH2O:      180,
    reactor_temp_c:     40.2,
    pH:                 8.5,
    flow_nm3_hr:        10000,
  },
  current_setpoints: { reactor_temp_c: 40, pH: 8.5 },
  performance: {
    co2_capture_pct:  87.2,
    so2_capture_pct:  96.8,
  },
  active_alerts:  [],
  uptime_seconds: 3600,
  last_update:    "2026-07-12T04:00:00Z",
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("LiveKPIGrid", () => {
  it("renders all six KPI labels", () => {
    render(<LiveKPIGrid state={base} />);
    expect(screen.getByText("CO₂ Capture")).toBeInTheDocument();
    expect(screen.getByText("SO₂ Capture")).toBeInTheDocument();
    expect(screen.getByText("Reactor Temp")).toBeInTheDocument();
    expect(screen.getByText("Mesh ΔP")).toBeInTheDocument();
    expect(screen.getByText("CO₂ Outlet")).toBeInTheDocument();
    expect(screen.getByText("SO₂ Outlet")).toBeInTheDocument();
  });

  it("displays the correct CO₂ capture value", () => {
    render(<LiveKPIGrid state={base} />);
    // 87.2 formatted to 1 decimal
    expect(screen.getByText("87.2")).toBeInTheDocument();
  });

  it("displays the correct Mesh ΔP value", () => {
    render(<LiveKPIGrid state={base} />);
    expect(screen.getByText("180.0")).toBeInTheDocument();
  });

  it("applies critical class when mesh_dp_mmH2O >= 240", () => {
    const critical: TwinState = {
      ...base,
      current_actuals: { ...base.current_actuals, mesh_dp_mmH2O: 250 },
    };
    const { container } = render(<LiveKPIGrid state={critical} />);
    // The critical tile has border-l-red-500
    expect(container.querySelector(".border-l-red-500")).toBeInTheDocument();
  });

  it("applies good class when mesh_dp_mmH2O < 200", () => {
    const { container } = render(<LiveKPIGrid state={base} />);
    expect(container.querySelector(".border-l-emerald-500")).toBeInTheDocument();
  });

  it("renders as a list with correct ARIA role", () => {
    render(<LiveKPIGrid state={base} />);
    expect(screen.getByRole("list", { name: "Real-time performance metrics" })).toBeInTheDocument();
  });

  it("shows SO₂ outlet as critical when >= 200 mg/Nm³", () => {
    const highSO2: TwinState = {
      ...base,
      current_actuals: { ...base.current_actuals, so2_outlet_mg_nm3: 250 },
    };
    const { container } = render(<LiveKPIGrid state={highSO2} />);
    const criticals = container.querySelectorAll(".border-l-red-500");
    expect(criticals.length).toBeGreaterThanOrEqual(1);
  });

  it("shows warning class when co2_capture_pct is between 60 and 80", () => {
    const warn: TwinState = {
      ...base,
      performance: { ...base.performance, co2_capture_pct: 70 },
    };
    const { container } = render(<LiveKPIGrid state={warn} />);
    expect(container.querySelector(".border-l-amber-500")).toBeInTheDocument();
  });
});
