/**
 * packages/web/src/features/operator/__tests__/AlertBanner.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AlertBanner } from "../components/AlertBanner";
import type { AlertData } from "../../../types/ws";

function makeAlert(id: string, severity: AlertData["severity"]): AlertData {
  return { alert_id: id, severity, title: `${severity} alert`, message: `${severity} message`, triggered_at: new Date().toISOString() };
}

describe("AlertBanner — hidden when empty", () => {
  it("renders nothing when alerts array is empty", () => {
    const { container } = render(<AlertBanner alerts={[]} />);
    expect(container.firstChild).toBeNull();
  });
});

describe("AlertBanner — with alerts", () => {
  const alerts = [makeAlert("a1", "HIGH"), makeAlert("a2", "MEDIUM")];

  it("shows alert count in text", () => {
    render(<AlertBanner alerts={alerts} />);
    expect(screen.getByText(/2 ALERTS/i)).toBeInTheDocument();
  });

  it("shows the first alert title", () => {
    render(<AlertBanner alerts={alerts} />);
    expect(screen.getByText(/HIGH alert/)).toBeInTheDocument();
  });

  it("applies red background for CRITICAL alerts", () => {
    const { container } = render(
      <AlertBanner alerts={[makeAlert("c1", "CRITICAL")]} />
    );
    expect(container.querySelector(".bg-red-900\\/90")).toBeInTheDocument();
  });

  it("applies amber background for non-critical alerts", () => {
    const { container } = render(<AlertBanner alerts={alerts} />);
    expect(container.querySelector(".bg-amber-900\\/90")).toBeInTheDocument();
  });

  it("calls onView when View button clicked", () => {
    const onView = vi.fn();
    render(<AlertBanner alerts={alerts} onView={onView} />);
    fireEvent.click(screen.getByRole("button", { name: /view all alerts/i }));
    expect(onView).toHaveBeenCalledTimes(1);
  });

  it("calls onDismiss when dismiss button clicked", () => {
    const onDismiss = vi.fn();
    render(<AlertBanner alerts={alerts} onDismiss={onDismiss} />);
    fireEvent.click(screen.getByRole("button", { name: /dismiss/i }));
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("has role=alert for screen readers", () => {
    render(<AlertBanner alerts={alerts} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("prioritises CRITICAL over HIGH in label", () => {
    const mixed = [makeAlert("h1", "HIGH"), makeAlert("c1", "CRITICAL")];
    render(<AlertBanner alerts={mixed} />);
    expect(screen.getByText(/1 CRITICAL/)).toBeInTheDocument();
  });
});
