/**
 * packages/web/src/features/simulation-results/__tests__/UncertaintyBadge.test.tsx
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UncertaintyBadge } from "../components/uncertainty/UncertaintyBadge";

describe("UncertaintyBadge — rendering", () => {
  it("renders ±X% format for percentage unit", () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" />);
    expect(screen.getByText(/±4\.5%/)).toBeInTheDocument();
  });

  it("renders ±X format with no unit", () => {
    render(<UncertaintyBadge ci90HalfWidth={2.0} />);
    expect(screen.getByText(/±2\.0/)).toBeInTheDocument();
  });

  it("renders with 1 decimal place", () => {
    render(<UncertaintyBadge ci90HalfWidth={6.78} unit=" MPa" />);
    // 6.78 → toFixed(1) = 6.8
    expect(screen.getByText(/±6\.8/)).toBeInTheDocument();
  });
});

describe("UncertaintyBadge — aria", () => {
  it("has aria-label mentioning uncertainty", () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" cv={0.05} />);
    const btn = screen.getByRole("button");
    expect(btn).toHaveAttribute("aria-label");
    expect(btn.getAttribute("aria-label")).toMatch(/uncertainty/i);
  });

  it("aria-expanded=false when popover closed", () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
  });
});

describe("UncertaintyBadge — popover interaction", () => {
  it("opens popover on click and shows '90% Confidence Interval' heading", () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" cv={0.08} />);
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByText("90% Confidence Interval")).toBeInTheDocument();
  });

  it("shows the CI value inside the popover", () => {
    render(<UncertaintyBadge ci90HalfWidth={6.7} unit="%" cv={0.08} />);
    fireEvent.click(screen.getByRole("button"));
    // ±6.7% appears in both the badge button AND the popover text span — use getAllByText
    const matches = screen.getAllByText(/±6\.7%/);
    expect(matches.length).toBeGreaterThanOrEqual(2);
    // The dialog should be open
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("closes popover on Escape key", async () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" cv={0.08} />);
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() =>
      expect(screen.queryByRole("dialog")).toBeNull()
    );
  });

  it("aria-expanded=true when popover is open", () => {
    render(<UncertaintyBadge ci90HalfWidth={4.5} unit="%" />);
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
  });
});

describe("UncertaintyBadge — confidence colouring (via cv)", () => {
  it("uses HIGH level for low cv", () => {
    render(<UncertaintyBadge ci90HalfWidth={1.0} unit="%" cv={0.04} />);
    // The button should have emerald text class
    const btn = screen.getByRole("button");
    expect(btn.className).toMatch(/emerald/);
  });

  it("uses LOW level for high cv", () => {
    render(<UncertaintyBadge ci90HalfWidth={30} unit="%" cv={0.5} />);
    const btn = screen.getByRole("button");
    expect(btn.className).toMatch(/red/);
  });

  it("defaults to MEDIUM when cv is undefined", () => {
    render(<UncertaintyBadge ci90HalfWidth={5.0} unit="%" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toMatch(/amber/);
  });
});
