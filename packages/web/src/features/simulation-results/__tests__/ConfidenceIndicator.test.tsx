/**
 * packages/web/src/features/simulation-results/__tests__/ConfidenceIndicator.test.tsx
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ConfidenceIndicator } from "../components/uncertainty/ConfidenceIndicator";

describe("ConfidenceIndicator — level classification", () => {
  it("shows HIGH for cv < 0.10", () => {
    render(<ConfidenceIndicator cv={0.05} />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("shows MEDIUM for cv between 0.10 and 0.25", () => {
    render(<ConfidenceIndicator cv={0.15} />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("shows LOW for cv ≥ 0.25", () => {
    render(<ConfidenceIndicator cv={0.40} />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("exactly 0.10 → MEDIUM (boundary check)", () => {
    render(<ConfidenceIndicator cv={0.10} />);
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("exactly 0.25 → LOW (boundary check)", () => {
    render(<ConfidenceIndicator cv={0.25} />);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });
});

describe("ConfidenceIndicator — accessibility", () => {
  it("has role=status for screen readers", () => {
    render(<ConfidenceIndicator cv={0.05} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("aria-label includes level and description", () => {
    render(<ConfidenceIndicator cv={0.05} />);
    const el = screen.getByRole("status");
    expect(el).toHaveAttribute("aria-label");
    expect(el.getAttribute("aria-label")).toMatch(/High confidence/i);
  });
});

describe("ConfidenceIndicator — CV display", () => {
  it("shows CV% when showCV=true", () => {
    render(<ConfidenceIndicator cv={0.082} showCV />);
    expect(screen.getByText(/8\.2%/)).toBeInTheDocument();
  });

  it("does not show CV by default", () => {
    render(<ConfidenceIndicator cv={0.082} />);
    expect(screen.queryByText(/8\.2%/)).toBeNull();
  });
});
