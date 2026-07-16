/**
 * packages/web/src/features/simulation-results/__tests__/KpiCard.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KpiCard } from "../components/KpiCard";
import type { UQMetric } from "../types/results";

function makeMetric(mean: number, cv: number): UQMetric {
  const std = mean * cv;
  const n = 200;
  const samples = Array.from({ length: n }, (_, i) => mean + ((i - n / 2) / n) * std * 6);
  const sorted = [...samples].sort((a, b) => a - b);
  const pct = (p: number) => sorted[Math.floor(n * p)];
  return {
    mean, std, cv,
    p5: pct(0.05), p25: pct(0.25), p50: pct(0.50),
    p75: pct(0.75), p95: pct(0.95),
    samples,
  };
}

const HIGH_METRIC   = makeMetric(87.2, 0.05);  // cv=0.05 → HIGH
const MEDIUM_METRIC = makeMetric(22.4, 0.15);  // cv=0.15 → MEDIUM
const LOW_METRIC    = makeMetric(5.0,  0.40);  // cv=0.40 → LOW

describe("KpiCard — rendering", () => {
  it("renders the label", () => {
    render(<KpiCard label="CO₂ Capture" metric={HIGH_METRIC} unit="%" />);
    expect(screen.getByText("CO₂ Capture")).toBeInTheDocument();
  });

  it("renders the mean value", () => {
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" precision={1} />);
    expect(screen.getByText("87.2")).toBeInTheDocument();
  });

  it("renders the unit", () => {
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" />);
    // Unit appears as a separate <span>
    expect(screen.getAllByText("%").length).toBeGreaterThan(0);
  });

  it("renders the ConfidenceIndicator pill", () => {
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("renders the UncertaintyBadge button", () => {
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" />);
    // UncertaintyBadge renders a <button>
    // KpiCard itself is a <button> → should be >= 2
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(2);
  });
});

describe("KpiCard — status border", () => {
  it("good border for value ≥ 95% of target", () => {
    const metric = makeMetric(90, 0.05);
    const { container } = render(
      <KpiCard label="Capture" metric={metric} unit="%" target={90} />
    );
    expect(container.querySelector(".border-l-emerald-500")).toBeInTheDocument();
  });

  it("critical border for value < 80% of target", () => {
    const metric = makeMetric(60, 0.05);
    const { container } = render(
      <KpiCard label="Capture" metric={metric} unit="%" target={85} />
    );
    expect(container.querySelector(".border-l-red-500")).toBeInTheDocument();
  });

  it("warning border for value between 80–95% of target", () => {
    const metric = makeMetric(75, 0.05);
    const { container } = render(
      <KpiCard label="Capture" metric={metric} unit="%" target={85} />
    );
    expect(container.querySelector(".border-l-amber-500")).toBeInTheDocument();
  });

  it("neutral border when no target given", () => {
    const { container } = render(
      <KpiCard label="Capture" metric={HIGH_METRIC} unit="%" />
    );
    expect(container.querySelector(".border-l-slate-600")).toBeInTheDocument();
  });
});

describe("KpiCard — target feedback", () => {
  it("shows ✓ Met when target met", () => {
    const metric = makeMetric(90, 0.05);
    render(<KpiCard label="Capture" metric={metric} unit="%" target={90} />);
    expect(screen.getByText(/✓ Met/)).toBeInTheDocument();
  });

  it("shows ✗ Critical when far below target", () => {
    const metric = makeMetric(60, 0.05);
    render(<KpiCard label="Capture" metric={metric} unit="%" target={85} />);
    expect(screen.getByText(/✗ Critical/)).toBeInTheDocument();
  });
});

describe("KpiCard — interaction", () => {
  it("calls onClick when card clicked", () => {
    const onClick = vi.fn();
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" onClick={onClick} />);
    // Click the outer button (first in DOM)
    const buttons = screen.getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("has accessible aria-label on the card", () => {
    render(<KpiCard label="CO₂ Capture" metric={HIGH_METRIC} unit="%" />);
    const buttons = screen.getAllByRole("button");
    // The KpiCard outer button should have an aria-label
    const cardBtn = buttons.find((b) => b.getAttribute("aria-label")?.includes("CO₂ Capture"));
    expect(cardBtn).toBeDefined();
  });
});

describe("KpiCard — confidence level colouring", () => {
  it("HIGH confidence → shows HIGH pill", () => {
    render(<KpiCard label="Capture" metric={HIGH_METRIC} unit="%" />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("MEDIUM confidence → shows MEDIUM pill", () => {
    render(<KpiCard label="Strength" metric={MEDIUM_METRIC} unit=" MPa" />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("LOW confidence → shows LOW pill", () => {
    render(<KpiCard label="IRR" metric={LOW_METRIC} unit="%" />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });
});
