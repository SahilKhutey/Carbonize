/**
 * packages/web/src/features/operator/__tests__/AlarmList.test.tsx
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AlarmList } from "../components/AlarmList";
import type { AlertData } from "../../../types/ws";

function makeAlert(id: string, severity: AlertData["severity"]): AlertData {
  return {
    alert_id: id,
    severity,
    title: `${severity} title`,
    message: `${severity} message`,
    triggered_at: "2026-07-12T04:00:00Z",
  };
}

const alerts = new Map<string, AlertData>([
  ["c1", makeAlert("c1", "CRITICAL")],
  ["h1", makeAlert("h1", "HIGH")],
  ["m1", makeAlert("m1", "MEDIUM")],
  ["l1", makeAlert("l1", "LOW")],
]);

describe("AlarmList — empty state", () => {
  it("shows 'No active alarms' message", () => {
    render(
      <AlarmList
        alerts={new Map()}
        onAcknowledge={vi.fn()}
        onEscalate={vi.fn()}
      />
    );
    expect(screen.getByText("No active alarms")).toBeInTheDocument();
  });
});

describe("AlarmList — with alarms", () => {
  it("renders all four alarms", () => {
    render(
      <AlarmList alerts={alerts} onAcknowledge={vi.fn()} onEscalate={vi.fn()} />
    );
    expect(screen.getByText(/CRITICAL title/)).toBeInTheDocument();
    expect(screen.getByText(/HIGH title/)).toBeInTheDocument();
    expect(screen.getByText(/MEDIUM title/)).toBeInTheDocument();
    expect(screen.getByText(/LOW title/)).toBeInTheDocument();
  });

  it("shows alarm count badge", () => {
    render(
      <AlarmList alerts={alerts} onAcknowledge={vi.fn()} onEscalate={vi.fn()} />
    );
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("does NOT show Acknowledge button when canAcknowledge=false", () => {
    render(
      <AlarmList
        alerts={alerts}
        onAcknowledge={vi.fn()}
        onEscalate={vi.fn()}
        canAcknowledge={false}
      />
    );
    expect(screen.queryByRole("button", { name: /acknowledge/i })).toBeNull();
  });

  it("shows Acknowledge buttons when canAcknowledge=true", () => {
    render(
      <AlarmList
        alerts={alerts}
        onAcknowledge={vi.fn()}
        onEscalate={vi.fn()}
        canAcknowledge={true}
      />
    );
    const ackBtns = screen.getAllByRole("button", { name: /acknowledge/i });
    expect(ackBtns.length).toBe(4);
  });

  it("shows Escalate buttons when canEscalate=true", () => {
    render(
      <AlarmList
        alerts={alerts}
        onAcknowledge={vi.fn()}
        onEscalate={vi.fn()}
        canEscalate={true}
      />
    );
    const escalateBtns = screen.getAllByRole("button", { name: /escalate/i });
    expect(escalateBtns.length).toBe(4);
  });

  it("opens ConfirmDialog when Acknowledge clicked", async () => {
    render(
      <AlarmList
        alerts={new Map([["c1", makeAlert("c1", "CRITICAL")]])}
        onAcknowledge={vi.fn()}
        onEscalate={vi.fn()}
        canAcknowledge={true}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /acknowledge/i }));
    await waitFor(() =>
      expect(screen.getByRole("dialog")).toBeInTheDocument()
    );
  });

  it("calls onAcknowledge after confirming dialog", async () => {
    const onAck = vi.fn();
    render(
      <AlarmList
        alerts={new Map([["c1", makeAlert("c1", "CRITICAL")]])}
        onAcknowledge={onAck}
        onEscalate={vi.fn()}
        canAcknowledge={true}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /acknowledge/i }));
    // Confirm dialog appears
    await waitFor(() => screen.getByRole("dialog"));
    // Click the Acknowledge confirm button inside dialog
    const confirmBtn = screen.getByRole("button", { name: /^acknowledge$/i });
    fireEvent.click(confirmBtn);
    await waitFor(() => expect(onAck).toHaveBeenCalledWith("c1"));
  });
});
