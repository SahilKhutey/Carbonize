/**
 * packages/web/src/features/simulation-results/__tests__/DistributionChart.test.tsx
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DistributionChart } from "../components/uncertainty/DistributionChart";

// 300 samples with normal distribution around 87.2
function makeSamples(mean = 87.2, std = 4.5, n = 300): number[] {
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    // Box-Muller (deterministic enough for tests)
    const u1 = ((i + 1) / (n + 1));
    const u2 = ((i * 7 + 3) % n) / n;
    const z = Math.sqrt(-2 * Math.log(u1 + 0.001)) * Math.cos(2 * Math.PI * u2);
    out.push(mean + z * std);
  }
  return out;
}

const SAMPLES = makeSamples();

describe("DistributionChart — rendering with data", () => {
  it("renders the chart title", () => {
    render(<DistributionChart title="CO₂ Capture" samples={SAMPLES} unit="%" />);
    expect(screen.getByText("CO₂ Capture")).toBeInTheDocument();
  });

  it("shows sample count", () => {
    render(<DistributionChart title="Test" samples={SAMPLES} unit="%" />);
    expect(screen.getByText(/300.*samples/i)).toBeInTheDocument();
  });

  it("renders the ConfidenceIndicator", () => {
    render(<DistributionChart title="Test" samples={SAMPLES} unit="%" />);
    // HIGH / MEDIUM / LOW should appear
    const indicator = screen.getByRole("status");
    expect(indicator).toBeInTheDocument();
  });

  it("shows 5 stat pills: P5, Median, Mean, P95, Std", () => {
    render(<DistributionChart title="Test" samples={SAMPLES} unit="%" />);
    expect(screen.getByText("P5")).toBeInTheDocument();
    expect(screen.getByText("Median")).toBeInTheDocument();
    expect(screen.getByText("Mean")).toBeInTheDocument();
    expect(screen.getByText("P95")).toBeInTheDocument();
    expect(screen.getByText("Std")).toBeInTheDocument();
  });

  it("stat values are numeric strings", () => {
    render(<DistributionChart title="Test" samples={SAMPLES} unit="%" />);
    // At least one element should render a decimal value near 87
    const elements = screen.getAllByText(/\d+\.\d\d/);
    expect(elements.length).toBeGreaterThan(0);
  });
});

describe("DistributionChart — empty state", () => {
  it("renders 'No distribution data available' for empty samples", () => {
    render(<DistributionChart title="Empty" samples={[]} />);
    expect(screen.getByText(/no distribution data/i)).toBeInTheDocument();
  });

  it("does not crash with a single sample", () => {
    render(<DistributionChart title="Single" samples={[42]} />);
    expect(screen.getByText("Single")).toBeInTheDocument();
  });
});

describe("DistributionChart — tight distribution gives HIGH confidence", () => {
  it("ConfidenceIndicator shows HIGH for tight distribution", () => {
    const tight = makeSamples(50, 0.1, 200); // CV ≈ 0.002
    render(<DistributionChart title="Tight" samples={tight} />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });
});

describe("DistributionChart — wide distribution gives LOW confidence", () => {
  it("ConfidenceIndicator shows LOW for wide distribution", () => {
    const wide = makeSamples(10, 5, 200); // CV ≈ 0.5
    render(<DistributionChart title="Wide" samples={wide} />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });
});
