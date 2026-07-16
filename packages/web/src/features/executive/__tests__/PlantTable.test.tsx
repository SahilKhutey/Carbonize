/**
 * packages/web/src/features/executive/__tests__/PlantTable.test.tsx
 */
import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { PlantTable } from "../components/PlantTable";
import type { PlantRow } from "../types/executive";

// Wrap with MemoryRouter because PlantTable uses useNavigate
const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

const plants: PlantRow[] = [
  { id: "p1", name: "Alpha Plant",  location: "Pune, MH",   status: "ok",      co2CapturePct: 87.2, npvCrorePerYear: 4.2, cctsTonnes: 450, lastMaintenanceDaysAgo: 12 },
  { id: "p2", name: "Beta Plant",   location: "Nashik, MH", status: "warning", co2CapturePct: 78.3, npvCrorePerYear: 3.8, cctsTonnes: 420, lastMaintenanceDaysAgo: 45 },
  { id: "p3", name: "Gamma Plant",  location: "Nagpur, MH", status: "fault",   co2CapturePct: 52.1, npvCrorePerYear: 1.2, cctsTonnes: 210, lastMaintenanceDaysAgo: 72 },
];

describe("PlantTable — rendering", () => {
  it("renders all plant rows", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    expect(screen.getByText("Alpha Plant")).toBeInTheDocument();
    expect(screen.getByText("Beta Plant")).toBeInTheDocument();
    expect(screen.getByText("Gamma Plant")).toBeInTheDocument();
  });

  it("shows location for each plant", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    expect(screen.getByText("Pune, MH")).toBeInTheDocument();
  });

  it("renders CO₂ capture % correctly", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    expect(screen.getByText("87.2%")).toBeInTheDocument();
  });

  it("renders status labels", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    // Status labels appear in the status column cells
    expect(screen.getAllByText("OK").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Warning").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Fault").length).toBeGreaterThanOrEqual(1);
  });

  it("has aria-label on the table", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    expect(screen.getByRole("table", { name: /plant portfolio/i })).toBeInTheDocument();
  });

  it("shows row count summary", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    expect(screen.getByText(/3 of 3 plants/)).toBeInTheDocument();
  });
});

describe("PlantTable — search filter", () => {
  it("filters by plant name", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    const search = screen.getByRole("searchbox", { name: /search plants/i });
    fireEvent.change(search, { target: { value: "Alpha" } });
    expect(screen.getByText("Alpha Plant")).toBeInTheDocument();
    expect(screen.queryByText("Beta Plant")).toBeNull();
    expect(screen.queryByText("Gamma Plant")).toBeNull();
  });

  it("shows 'No plants match' when no results", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    const search = screen.getByRole("searchbox", { name: /search plants/i });
    fireEvent.change(search, { target: { value: "Zork Plant" } });
    expect(screen.getByText(/no plants match/i)).toBeInTheDocument();
  });
});

describe("PlantTable — status filter", () => {
  it("filters to only 'warning' plants", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    const select = screen.getByRole("combobox", { name: /filter by status/i });
    fireEvent.change(select, { target: { value: "warning" } });
    expect(screen.queryByText("Alpha Plant")).toBeNull();
    expect(screen.getByText("Beta Plant")).toBeInTheDocument();
  });
});

describe("PlantTable — sorting", () => {
  it("sorts by CO₂ capture ascending on column click", () => {
    render(<PlantTable plants={plants} />, { wrapper: Wrapper });
    const co2Header = screen.getByText(/CO₂ Capture/i).closest("th")!;
    fireEvent.click(co2Header);
    // After ascending sort, Gamma (52.1) should come before Beta (78.3)
    const rows = screen.getAllByRole("row");
    const rowTexts = rows.slice(1).map((r) => within(r).queryByText(/Plant/)?.textContent ?? "");
    const gammaIdx = rowTexts.findIndex((t) => t.includes("Gamma"));
    const betaIdx  = rowTexts.findIndex((t) => t.includes("Beta"));
    expect(gammaIdx).toBeLessThan(betaIdx);
  });
});
