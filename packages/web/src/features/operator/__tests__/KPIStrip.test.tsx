/**
 * packages/web/src/features/operator/__tests__/KPIStrip.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KPIStrip } from "../components/KPIStrip";
import type { TwinState } from "../../digital-twin/types/twin";

const base: TwinState = {
  plant_id: "p1", org_id: "o1",
  operating_mode: "running",
  current_actuals: {
    co2_inlet_pct: 14, co2_outlet_pct: 1.8, so2_inlet_mg_nm3: 1200,
    so2_outlet_mg_nm3: 38, mesh_dp_mmH2O: 180, reactor_temp_c: 40.2,
    pH: 8.5, flow_nm3_hr: 10000,
  },
  current_setpoints: { reactor_temp_c: 40, pH: 8.5 },
  performance: { co2_capture_pct: 87.2, so2_capture_pct: 96.8 },
  active_alerts: [],
  uptime_seconds: 3600,
  last_update: "2026-07-12T04:00:00Z",
};

describe("KPIStrip — rendering", () => {
  it("renders 6 KPI tiles", () => {
    render(<KPIStrip state={base} />);
    // Each tile is a button
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(6);
  });

  it("shows CO₂ Capture label", () => {
    render(<KPIStrip state={base} />);
    expect(screen.getByText("CO₂ Capture")).toBeInTheDocument();
  });

  it("shows Mesh ΔP value (180)", () => {
    render(<KPIStrip state={base} />);
    expect(screen.getByText("180")).toBeInTheDocument();
  });

  it("shows SO₂ Outlet unit label", () => {
    render(<KPIStrip state={base} />);
    expect(screen.getByText("mg/Nm³")).toBeInTheDocument();
  });
});

describe("KPIStrip — status colouring", () => {
  it("SO₂ Outlet tile is critical when >= 200 mg/Nm³", () => {
    const critical: TwinState = {
      ...base,
      current_actuals: { ...base.current_actuals, so2_outlet_mg_nm3: 250 },
    };
    const { container } = render(<KPIStrip state={critical} />);
    expect(container.querySelector(".border-red-500")).toBeInTheDocument();
  });

  it("Mesh ΔP is good when < 200 mmH₂O", () => {
    const { container } = render(<KPIStrip state={base} />);
    expect(container.querySelector(".border-emerald-500")).toBeInTheDocument();
  });

  it("Mesh ΔP is warning when 200–239", () => {
    const warn: TwinState = {
      ...base,
      current_actuals: { ...base.current_actuals, mesh_dp_mmH2O: 220 },
    };
    const { container } = render(<KPIStrip state={warn} />);
    expect(container.querySelector(".border-amber-500")).toBeInTheDocument();
  });
});

describe("KPIStrip — interaction", () => {
  it("calls onTileClick with metric id when tile clicked", () => {
    const onClick = vi.fn();
    render(<KPIStrip state={base} onTileClick={onClick} />);
    // Click the CO₂ Capture tile (first button)
    fireEvent.click(screen.getAllByRole("button")[0]);
    expect(onClick).toHaveBeenCalledWith("co2_capture");
  });

  it("each button has an aria-label", () => {
    render(<KPIStrip state={base} />);
    const buttons = screen.getAllByRole("button");
    buttons.forEach((btn) => {
      expect(btn).toHaveAttribute("aria-label");
    });
  });
});
