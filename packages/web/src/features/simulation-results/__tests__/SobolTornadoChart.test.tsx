/**
 * packages/web/src/features/simulation-results/__tests__/SobolTornadoChart.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SobolTornadoChart } from "../components/uncertainty/SobolTornadoChart";
import type { SobolIndex } from "../types/results";

const indices: SobolIndex[] = [
  { parameter: "enzyme_conc", label: "Enzyme concentration",  s1: 0.28, s1_conf: 0.02, st: 0.35, st_conf: 0.03, current_uncertainty: "±30%" },
  { parameter: "ca2_conc",    label: "Ca²⁺ concentration",   s1: 0.18, s1_conf: 0.02, st: 0.22, st_conf: 0.02, current_uncertainty: "±20%" },
  { parameter: "ph_sp",       label: "pH setpoint",           s1: 0.12, s1_conf: 0.01, st: 0.15, st_conf: 0.01 },
  { parameter: "temp",        label: "Reactor temperature",   s1: 0.07, s1_conf: 0.01, st: 0.10, st_conf: 0.01 },
  { parameter: "flow_rate",   label: "Gas flow rate",         s1: 0.05, s1_conf: 0.01, st: 0.08, st_conf: 0.01 },
  { parameter: "co2_inlet",   label: "CO₂ inlet %",          s1: 0.04, s1_conf: 0.01, st: 0.06, st_conf: 0.01 },
];

describe("SobolTornadoChart — rendering", () => {
  it("renders the title", () => {
    render(
      <SobolTornadoChart outputName="CO₂ Capture" outputUnit="%" indices={indices} />
    );
    expect(screen.getByText("Sensitivity Analysis")).toBeInTheDocument();
  });

  it("renders outputName in the subtitle", () => {
    render(
      <SobolTornadoChart outputName="CO₂ Capture" outputUnit="%" indices={indices} />
    );
    expect(screen.getByText(/CO₂ Capture/)).toBeInTheDocument();
  });

  it("renders all parameter labels in chart", () => {
    render(
      <SobolTornadoChart outputName="CO₂ Capture" indices={indices} />
    );
    expect(screen.getByText("Enzyme concentration")).toBeInTheDocument();
    expect(screen.getByText("Ca²⁺ concentration")).toBeInTheDocument();
  });

  it("shows the 'Sobol method' badge", () => {
    render(<SobolTornadoChart outputName="NPV" indices={indices} />);
    expect(screen.getByText(/Sobol method/)).toBeInTheDocument();
  });

  it("renders the variance summary box", () => {
    render(<SobolTornadoChart outputName="CO₂ Capture" indices={indices} />);
    expect(screen.getByText(/Top 5 parameters explain/)).toBeInTheDocument();
  });

  it("renders the critical experiments list", () => {
    render(<SobolTornadoChart outputName="CO₂ Capture" indices={indices} />);
    expect(screen.getByRole("list", { name: /critical experiments/i })).toBeInTheDocument();
  });

  it("shows top-5 critical experiment items", () => {
    render(<SobolTornadoChart outputName="CO₂ Capture" indices={indices} />);
    const items = screen.getAllByRole("listitem");
    expect(items.length).toBe(5);
  });
});

describe("SobolTornadoChart — sorted order", () => {
  it("renders enzyme concentration first (highest ST)", () => {
    render(<SobolTornadoChart outputName="CO₂ Capture" indices={indices} />);
    const items = screen.getAllByRole("listitem");
    expect(items[0].textContent).toMatch(/Enzyme concentration/);
  });
});

describe("SobolTornadoChart — interaction", () => {
  it("calls onParameterClick when a critical experiment item is clicked", () => {
    const onClick = vi.fn();
    render(
      <SobolTornadoChart
        outputName="CO₂ Capture"
        indices={indices}
        onParameterClick={onClick}
      />
    );
    const items = screen.getAllByRole("listitem");
    fireEvent.click(items[0]);
    expect(onClick).toHaveBeenCalledWith("enzyme_conc");
  });
});

describe("SobolTornadoChart — show all toggle", () => {
  it("shows 'Show all' button when indices > maxShown", () => {
    render(
      <SobolTornadoChart
        outputName="CO₂ Capture"
        indices={indices}
        maxShown={3}
      />
    );
    expect(screen.getByText(/show all/i)).toBeInTheDocument();
  });

  it("does not show 'Show all' button when all fit within maxShown", () => {
    render(
      <SobolTornadoChart
        outputName="CO₂ Capture"
        indices={indices}
        maxShown={20}
      />
    );
    expect(screen.queryByText(/show all/i)).toBeNull();
  });

  it("shows 'Show fewer' after expanding", () => {
    render(
      <SobolTornadoChart
        outputName="CO₂ Capture"
        indices={indices}
        maxShown={3}
      />
    );
    fireEvent.click(screen.getByText(/show all/i));
    // After expanding, the toggle button changes to "Show fewer"
    expect(screen.getByText(/show fewer/i)).toBeInTheDocument();
    // "Show all" should no longer be there
    expect(screen.queryByText(/show all.*parameters/i)).toBeNull();
  });
});
