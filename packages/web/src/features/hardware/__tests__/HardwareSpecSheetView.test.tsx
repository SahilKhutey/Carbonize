import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { HardwareSpecSheetView, HardwareSpecData } from "../HardwareSpecSheetView";

const mockSpec: HardwareSpecData = {
  project_name: "CBMS Pilot Unit Sizing Handoff",
  target_flue_gas_flow_nm3_hr: 10000.0,
  target_co2_capture_pct: 85.0,
  reactor_volume_m3: 91.2,
  column_diameter_m: 3.1,
  column_height_m: 12.0,
  residence_time_s: 27.0,
  liquid_to_gas_ratio_l_per_nm3: 8.5,
  applied_safety_margin_pct: 15.0,
  sized_reactor_volume_m3: 104.88,
  chitosan_wt_pct: 3.0,
  chitosan_consumption_kg_per_day: 125.0,
  ca_lime_consumption_kg_per_day: 450.0,
  ca_enzyme_dosage_mg_per_l: 12.0,
  mesh_replacement_interval_days: 90,
  trust_score: {
    trust_level: "HIGH_CONFIDENCE_VALIDATED",
    provenance_status: "🟢 Bench-validated",
    comparator_status: "VALIDATED",
    ci_90_coverage_pct: 95.0,
    recommended_safety_margin_pct: 15.0,
    hardware_guidance_text: "Model predictions match pilot bench data.",
  },
};

describe("HardwareSpecSheetView Component", () => {
  it("renders project title and target flow rate", () => {
    render(<HardwareSpecSheetView spec={mockSpec} />);
    expect(screen.getByText("CBMS Pilot Unit Sizing Handoff")).toBeInTheDocument();
    expect(screen.getByText("10,000")).toBeInTheDocument();
  });

  it("displays trust score badge and safety margin", () => {
    render(<HardwareSpecSheetView spec={mockSpec} />);
    expect(screen.getByText("HIGH_CONFIDENCE_VALIDATED")).toBeInTheDocument();
    expect(screen.getByText("Margin: +15%")).toBeInTheDocument();
  });

  it("displays sized reactor volume and consumables", () => {
    render(<HardwareSpecSheetView spec={mockSpec} />);
    expect(screen.getByText("104.88")).toBeInTheDocument();
    expect(screen.getByText("125")).toBeInTheDocument();
  });
});
