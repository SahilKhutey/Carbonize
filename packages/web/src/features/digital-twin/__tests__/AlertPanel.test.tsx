/**
 * packages/web/src/features/digital-twin/__tests__/AlertPanel.test.tsx
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AlertPanel } from "../components/AlertPanel";
import { AlertData } from "../../../types/ws";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeAlert(id: string, severity: AlertData["severity"]): AlertData {
  return {
    alert_id:      id,
    severity,
    title:         `${severity} alert`,
    message:       `${severity} message`,
    triggered_at:  "2026-07-12T04:00:00Z",
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("AlertPanel — empty state", () => {
  it("shows 'No active alerts' when map is empty", () => {
    render(<AlertPanel alerts={new Map()} onAcknowledge={vi.fn()} />);
    expect(screen.getByText("No active alerts")).toBeInTheDocument();
    expect(screen.getByText("All systems normal")).toBeInTheDocument();
  });

  it("does not render any acknowledge buttons when empty", () => {
    render(<AlertPanel alerts={new Map()} onAcknowledge={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /acknowledge/i })).toBeNull();
  });
});

describe("AlertPanel — with alerts", () => {
  const alerts = new Map<string, AlertData>([
    ["a-low",      makeAlert("a-low",      "LOW")],
    ["a-critical", makeAlert("a-critical", "CRITICAL")],
    ["a-medium",   makeAlert("a-medium",   "MEDIUM")],
    ["a-high",     makeAlert("a-high",     "HIGH")],
  ]);

  it("renders alerts sorted CRITICAL → HIGH → MEDIUM → LOW", () => {
    render(<AlertPanel alerts={alerts} onAcknowledge={vi.fn()} />);
    const titles = screen
      .getAllByRole("listitem")
      .map((el) => el.querySelector("p")?.textContent ?? "");

    const order = titles.indexOf("CRITICAL alert");
    const orderH = titles.indexOf("HIGH alert");
    const orderM = titles.indexOf("MEDIUM alert");
    const orderL = titles.indexOf("LOW alert");

    expect(order).toBeLessThan(orderH);
    expect(orderH).toBeLessThan(orderM);
    expect(orderM).toBeLessThan(orderL);
  });

  it("shows badge count equal to number of alerts", () => {
    render(<AlertPanel alerts={alerts} onAcknowledge={vi.fn()} />);
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("calls onAcknowledge with correct alertId when button clicked", async () => {
    const onAck = vi.fn();
    const single = new Map<string, AlertData>([
      ["a-1", makeAlert("a-1", "HIGH")],
    ]);
    render(<AlertPanel alerts={single} onAcknowledge={onAck} />);

    const btn = screen.getByRole("button", { name: /acknowledge/i });
    fireEvent.click(btn);

    await waitFor(() => expect(onAck).toHaveBeenCalledWith("a-1"));
  });

  it("disables acknowledge button while acking", async () => {
    const onAck = vi.fn();
    const single = new Map<string, AlertData>([
      ["a-1", makeAlert("a-1", "HIGH")],
    ]);
    render(<AlertPanel alerts={single} onAcknowledge={onAck} />);

    const btn = screen.getByRole("button", { name: /acknowledge/i });
    fireEvent.click(btn);
    expect(btn).toBeDisabled();
  });

  it("renders recommended_action when present", () => {
    const withAction = new Map<string, AlertData>([
      ["b-1", {
        ...makeAlert("b-1", "MEDIUM"),
        recommended_action: "Check valve V-03",
      }],
    ]);
    render(<AlertPanel alerts={withAction} onAcknowledge={vi.fn()} />);
    expect(screen.getByText(/Check valve V-03/)).toBeInTheDocument();
  });
});

describe("AlertPanel — accessibility", () => {
  it("has role=list on the alert container", () => {
    const alerts = new Map<string, AlertData>([
      ["a-1", makeAlert("a-1", "LOW")],
    ]);
    render(<AlertPanel alerts={alerts} onAcknowledge={vi.fn()} />);
    expect(screen.getByRole("list", { name: /active alerts/i })).toBeInTheDocument();
  });
});
