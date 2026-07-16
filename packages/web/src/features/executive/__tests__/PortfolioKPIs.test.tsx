/**
 * packages/web/src/features/executive/__tests__/PortfolioKPIs.test.tsx
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PortfolioKPIs } from "../components/PortfolioKPIs";
import type { PortfolioSummary } from "../types/executive";

const data: PortfolioSummary = {
  lastUpdated: "2026-07-12T04:00:00Z",
  kpis: [
    { id: "co2", label: "CO₂ Captured", value: "2,847", unit: "tonnes", changePct: 12,  periodLabel: "Month-to-Date", trend: "up"   },
    { id: "ccts", label: "CCTS Credits", value: "₹52L",  unit: "",       changePct: 8,   periodLabel: "Year-to-Date",  trend: "up"   },
    { id: "savings", label: "Savings",   value: "₹18 Cr",unit: "",       changePct: -3,  periodLabel: "YoY",           trend: "down" },
    { id: "plants", label: "Plants",     value: "23",    unit: "",       changePct: 0,   periodLabel: "",              trend: "flat" },
    { id: "cap",  label: "Avg Capture",  value: "85.4",  unit: "%",      changePct: 2.1, periodLabel: "vs Q2",         trend: "up"   },
    { id: "int",  label: "Intensity",    value: "0.42",  unit: "tCO₂/MWh", changePct: -6.7, periodLabel: "YoY", trend: "down" },
  ],
};

describe("PortfolioKPIs", () => {
  it("renders all 6 KPI cards", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByText("CO₂ Captured")).toBeInTheDocument();
    expect(screen.getByText("CCTS Credits")).toBeInTheDocument();
    expect(screen.getByText("Savings")).toBeInTheDocument();
    expect(screen.getByText("Plants")).toBeInTheDocument();
    expect(screen.getByText("Avg Capture")).toBeInTheDocument();
    expect(screen.getByText("Intensity")).toBeInTheDocument();
  });

  it("renders correct KPI values", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByText("2,847")).toBeInTheDocument();
    expect(screen.getByText("23")).toBeInTheDocument();
    expect(screen.getByText("85.4")).toBeInTheDocument();
  });

  it("renders unit when provided", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByText("tonnes")).toBeInTheDocument();
    expect(screen.getByText("%")).toBeInTheDocument();
  });

  it("renders period labels", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByText("Month-to-Date")).toBeInTheDocument();
    expect(screen.getByText("Year-to-Date")).toBeInTheDocument();
  });

  it("shows positive change as +12.0%", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByLabelText(/\+12\.0% trend/i)).toBeInTheDocument();
  });

  it("shows negative change as -3.0%", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByLabelText(/-3\.0% trend/i)).toBeInTheDocument();
  });

  it("does not render trend for flat/zero change", () => {
    render(<PortfolioKPIs data={data} />);
    // changePct === 0 for "Plants" → no trend span rendered
    // Simply verify the Plants card has no +/- text
    const plantsCard = screen.getByText("Plants").closest("div");
    expect(plantsCard?.textContent).not.toMatch(/\+0\.0%|-0\.0%/);
  });

  it("has section role with correct aria-label", () => {
    render(<PortfolioKPIs data={data} />);
    expect(screen.getByRole("region", { name: /portfolio kpis/i })).toBeInTheDocument();
  });
});
