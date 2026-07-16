/**
 * packages/web/src/features/executive/__tests__/AutoInsights.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter, useNavigate } from "react-router-dom";
import { AutoInsights } from "../components/AutoInsights";
import type { AutoInsight } from "../types/executive";

// Mock react-router navigate
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: vi.fn() };
});

const insights: AutoInsight[] = [
  {
    id: "i1", plantId: "p1", plantName: "Plant A",
    title: "CO₂ capture fell 8% in week 14",
    summary: "Enzyme concentration drift suspected.",
    severity: "warning",
    detectedAt: "2026-07-12T09:00:00Z",
    drillDownUrl: "/executive/plants/p1",
  },
  {
    id: "i2", plantId: "p2", plantName: "Plant B",
    title: "NPV on track to exceed projection",
    summary: "CCTS price trending above budget.",
    severity: "opportunity",
    detectedAt: "2026-07-12T10:00:00Z",
    drillDownUrl: "/executive/plants/p2",
  },
  {
    id: "i3", plantId: "p3", plantName: "Plant C",
    title: "Maintenance window upcoming",
    summary: "Scheduled in 48 hours.",
    severity: "info",
    detectedAt: "2026-07-12T11:00:00Z",
  },
];

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

describe("AutoInsights — empty", () => {
  it("renders nothing when insights array is empty", () => {
    const { container } = render(<AutoInsights insights={[]} />, { wrapper: Wrapper });
    expect(container.firstChild).toBeNull();
  });
});

describe("AutoInsights — rendering", () => {
  it("shows all insight titles", () => {
    render(<AutoInsights insights={insights} />, { wrapper: Wrapper });
    expect(screen.getByText("CO₂ capture fell 8% in week 14")).toBeInTheDocument();
    expect(screen.getByText("NPV on track to exceed projection")).toBeInTheDocument();
    expect(screen.getByText("Maintenance window upcoming")).toBeInTheDocument();
  });

  it("shows summaries", () => {
    render(<AutoInsights insights={insights} />, { wrapper: Wrapper });
    expect(screen.getByText("Enzyme concentration drift suspected.")).toBeInTheDocument();
  });

  it("shows plant names", () => {
    render(<AutoInsights insights={insights} />, { wrapper: Wrapper });
    expect(screen.getByText("Plant A")).toBeInTheDocument();
    expect(screen.getByText("Plant B")).toBeInTheDocument();
  });

  it("shows severity badge labels", () => {
    render(<AutoInsights insights={insights} />, { wrapper: Wrapper });
    expect(screen.getByText("Warning")).toBeInTheDocument();
    expect(screen.getByText("Opportunity")).toBeInTheDocument();
    expect(screen.getByText("Info")).toBeInTheDocument();
  });

  it("shows Drill Down link for insights with drillDownUrl", () => {
    render(<AutoInsights insights={insights} />, { wrapper: Wrapper });
    const links = screen.getAllByText("Drill Down →");
    expect(links).toHaveLength(2); // i1 and i2 have drillDownUrl, i3 does not
  });

  it("does NOT show Drill Down for insight without drillDownUrl", () => {
    render(<AutoInsights insights={[insights[2]]} />, { wrapper: Wrapper });
    expect(screen.queryByText("Drill Down →")).toBeNull();
  });

  it("calls navigate when Drill Down clicked", () => {
    const mockNavigate = vi.fn();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
    render(<AutoInsights insights={[insights[0]]} />, { wrapper: Wrapper });
    fireEvent.click(screen.getByText("Drill Down →"));
    expect(mockNavigate).toHaveBeenCalledWith("/executive/plants/p1");
  });
});
