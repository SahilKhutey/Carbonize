/**
 * packages/web/src/features/simulation/__tests__/SimulationList.test.tsx
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { SimulationList } from "../pages/SimulationList";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockRunsData = [
  {
    id: "sim-001-mock",
    status: "COMPLETED",
    created_at: "2026-07-15T08:30:00Z",
    completed_at: "2026-07-15T08:44:20Z",
    plant: { name: "Alpha Plant" }
  },
  {
    id: "sim-002-mock",
    status: "FAILED",
    created_at: "2026-07-15T09:15:00Z",
    completed_at: "2026-07-15T09:17:10Z",
    plant: { name: "Beta Plant" }
  }
];

describe("SimulationList", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRunsData,
    });
  });

  const renderList = () =>
    render(
      <BrowserRouter>
        <SimulationList />
      </BrowserRouter>
    );

  it("renders the title and new simulation button", async () => {
    renderList();
    expect(await screen.findByText("Simulations")).toBeInTheDocument();
    expect(await screen.findByText("New Simulation")).toBeInTheDocument();
  });

  it("renders the mock simulation rows", async () => {
    renderList();
    expect(await screen.findByText("Run #sim-001- (Alpha Plant)")).toBeInTheDocument();
    expect(await screen.findByText("Run #sim-002- (Beta Plant)")).toBeInTheDocument();
  });

  it("navigates to new simulation when CTA clicked", async () => {
    renderList();
    const btn = await screen.findByText("New Simulation");
    fireEvent.click(btn);
    expect(mockNavigate).toHaveBeenCalledWith("/simulations/new");
  });

  it("filters correctly", async () => {
    renderList();
    
    const select = await screen.findByRole("combobox");
    fireEvent.change(select, { target: { value: "FAILED" } });
    
    expect(await screen.findByText("Run #sim-002- (Beta Plant)")).toBeInTheDocument();
    expect(screen.queryByText("Run #sim-001- (Alpha Plant)")).toBeNull();
  });
});
