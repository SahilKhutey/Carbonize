import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { ShiftHandover } from "../pages/ShiftHandover";

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

describe("ShiftHandover form component", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders form controls and auto-generated summary logs", () => {
    render(<ShiftHandover />, { wrapper: Wrapper });

    expect(screen.getByText("Shift Handover")).toBeInTheDocument();
    expect(screen.getByLabelText(/outgoing operator/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/incoming operator/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/operator notes/i)).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("CO₂ capture avg: 87.2%"))).toBeInTheDocument();
  });

  it("posts to backend handover endpoint and displays success status", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ status: "success" }),
    } as Response);

    render(<ShiftHandover />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText(/outgoing operator/i), {
      target: { value: "John Doe" },
    });
    fireEvent.change(screen.getByLabelText(/incoming operator/i), {
      target: { value: "Jane Smith" },
    });
    fireEvent.change(screen.getByLabelText(/operator notes/i), {
      target: { value: "Everything is stable. Reagent tanks at 80%." },
    });

    const submitBtn = screen.getByRole("button", { name: /sign off & submit/i });
    fireEvent.click(submitBtn);

    expect(screen.getByText("Saving…")).toBeInTheDocument();

    await screen.findByText("Shift Handed Over");
    expect(screen.getByText("Handover note saved. Incoming operator notified.")).toBeInTheDocument();

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/operator/handover",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          outgoing_operator: "John Doe",
          incoming_operator: "Jane Smith",
          notes: "Everything is stable. Reagent tanks at 80%.",
          shift_summary: [
            "CO₂ capture avg: 87.2% (target: ≥ 85%) ✅",
            "SO₂ capture avg: 96.5% ✅",
            "2 alarms raised — 2 acknowledged",
            "Pump A stopped 09:32, restarted 09:48 (reagent slug cleared)",
            "Reactor temp stable at 40.2 °C ± 0.4 °C",
          ]
        })
      })
    );
  });

  it("displays error message if form submission fails", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    render(<ShiftHandover />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText(/outgoing operator/i), {
      target: { value: "John Doe" },
    });
    fireEvent.change(screen.getByLabelText(/incoming operator/i), {
      target: { value: "Jane Smith" },
    });

    const submitBtn = screen.getByRole("button", { name: /sign off & submit/i });
    fireEvent.click(submitBtn);

    await screen.findByText("Failed to save handover. Please try again.");
  });
});
