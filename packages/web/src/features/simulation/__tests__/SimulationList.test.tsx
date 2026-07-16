/**
 * packages/web/src/features/simulation/__tests__/SimulationList.test.tsx
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
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

describe("SimulationList", () => {
  const renderList = () =>
    render(
      <BrowserRouter>
        <SimulationList />
      </BrowserRouter>
    );

  it("renders the title and new simulation button", () => {
    renderList();
    expect(screen.getByText("Simulations")).toBeInTheDocument();
    expect(screen.getByText("New Simulation")).toBeInTheDocument();
  });

  it("renders the mock simulation rows", () => {
    renderList();
    // We expect some of the mock names
    expect(screen.getByText("High-Temp Stress Test")).toBeInTheDocument();
    expect(screen.getByText("Winter Flow Rate Opt")).toBeInTheDocument();
  });

  it("navigates to new simulation when CTA clicked", () => {
    renderList();
    fireEvent.click(screen.getByText("New Simulation"));
    expect(mockNavigate).toHaveBeenCalledWith("/simulations/new");
  });

  it("filters correctly", () => {
    renderList();
    
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "FAILED" } });
    
    // Only the failed one should be visible
    expect(screen.getByText("Winter Flow Rate Opt")).toBeInTheDocument();
    expect(screen.queryByText("High-Temp Stress Test")).toBeNull();
  });
});
