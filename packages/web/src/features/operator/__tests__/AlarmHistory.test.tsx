import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AlarmHistory } from "../pages/AlarmHistory";

const mockAlarmsResponse = {
  alarms: [
    {
      id: "alarm-0",
      alert_id: "a-0",
      severity: "CRITICAL",
      title: "SO₂ outlet exceeded CPCB limit",
      message: "SO₂ outlet 215 mg/Nm³",
      triggered_at: "2026-07-18T10:00:00Z",
      resolved_at: "2026-07-18T10:08:00Z",
      resolved_by: "Operator A",
      resolution_method: "acknowledged",
    },
    {
      id: "alarm-1",
      alert_id: "a-1",
      severity: "HIGH",
      title: "Mesh ΔP approaching threshold",
      message: "Mesh ΔP 238 mmH₂O",
      triggered_at: "2026-07-18T10:10:00Z",
      resolved_at: undefined,
      resolved_by: undefined,
      resolution_method: undefined,
    }
  ],
  total: 2
};

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

describe("AlarmHistory page component", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders headers and loads alarms dynamically", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockAlarmsResponse,
    } as Response);

    render(<AlarmHistory />, { wrapper: Wrapper });

    expect(screen.getByText("Alarm History")).toBeInTheDocument();
    expect(screen.getByText("Loading alarm records...")).toBeInTheDocument();

    await screen.findByText("SO₂ outlet exceeded CPCB limit");
    expect(screen.getByText("Mesh ΔP approaching threshold")).toBeInTheDocument();
    expect(screen.getByText("2 alarms")).toBeInTheDocument();
  });

  it("queries the API with selected severity filter", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ alarms: [mockAlarmsResponse.alarms[0]], total: 1 }),
    } as Response);

    render(<AlarmHistory />, { wrapper: Wrapper });

    await screen.findByText("SO₂ outlet exceeded CPCB limit");

    const select = screen.getByRole("combobox", { name: /filter by severity/i });
    fireEvent.change(select, { target: { value: "CRITICAL" } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/operator/alarms?severity=CRITICAL&page=0")
      );
    });
  });

  it("handles CSV export trigger correctly", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockAlarmsResponse,
    } as Response);

    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    const createObjectURLMock = vi.fn().mockReturnValue("blob:foo");
    const revokeObjectURLMock = vi.fn();
    
    vi.stubGlobal("URL", {
      createObjectURL: createObjectURLMock,
      revokeObjectURL: revokeObjectURLMock,
    });

    render(<AlarmHistory />, { wrapper: Wrapper });

    await screen.findByText("SO₂ outlet exceeded CPCB limit");

    const exportBtn = screen.getByRole("button", { name: /export alarm history as csv/i });
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/operator/alarms?severity=all&page=0&page_size=1000")
      );
      expect(clickSpy).toHaveBeenCalled();
    });

    clickSpy.mockRestore();
  });

  it("displays error banner on fetch failures", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      status: 500,
    } as Response);

    render(<AlarmHistory />, { wrapper: Wrapper });

    await screen.findByText("Failed to load alarms (Status 500)");
  });
});
