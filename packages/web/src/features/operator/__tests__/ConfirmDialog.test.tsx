/**
 * packages/web/src/features/operator/__tests__/ConfirmDialog.test.tsx
 */
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ConfirmDialog } from "../components/ConfirmDialog";

const BASE = {
  isOpen: true,
  title: "Start Pump A?",
  message: "This will start the reagent pump. Confirm only if safe.",
  onConfirm: vi.fn(),
  onCancel: vi.fn(),
};

describe("ConfirmDialog — closed state", () => {
  it("renders nothing when isOpen=false", () => {
    const { container } = render(
      <ConfirmDialog {...BASE} isOpen={false} />
    );
    expect(container.firstChild).toBeNull();
  });
});

describe("ConfirmDialog — open state", () => {
  it("shows title and message", () => {
    render(<ConfirmDialog {...BASE} />);
    expect(screen.getByText("Start Pump A?")).toBeInTheDocument();
    expect(screen.getByText(/confirm only if safe/i)).toBeInTheDocument();
  });

  it("has role=dialog", () => {
    render(<ConfirmDialog {...BASE} />);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("calls onConfirm when confirm button clicked", () => {
    const onConfirm = vi.fn();
    render(<ConfirmDialog {...BASE} onConfirm={onConfirm} />);
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when cancel button clicked", () => {
    const onCancel = vi.fn();
    render(<ConfirmDialog {...BASE} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when backdrop clicked", () => {
    const onCancel = vi.fn();
    render(<ConfirmDialog {...BASE} onCancel={onCancel} />);
    // backdrop is the div with aria-hidden
    const backdrop = document.querySelector("[aria-hidden='true']") as HTMLElement;
    fireEvent.click(backdrop);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when Escape key pressed", () => {
    const onCancel = vi.fn();
    render(<ConfirmDialog {...BASE} onCancel={onCancel} />);
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("uses amber confirm button for danger=true", () => {
    const { container } = render(
      <ConfirmDialog {...BASE} danger confirmLabel="Stop Equipment" />
    );
    const btn = container.querySelector("button.bg-amber-600");
    expect(btn).toBeInTheDocument();
    expect(btn?.textContent).toMatch(/stop equipment/i);
  });

  it("uses green confirm button for danger=false (default)", () => {
    const { container } = render(<ConfirmDialog {...BASE} />);
    expect(container.querySelector("button.bg-emerald-600")).toBeInTheDocument();
  });

  it("uses custom confirmLabel and cancelLabel", () => {
    render(
      <ConfirmDialog
        {...BASE}
        confirmLabel="Yes, do it"
        cancelLabel="No, abort"
      />
    );
    expect(screen.getByRole("button", { name: /yes, do it/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /no, abort/i })).toBeInTheDocument();
  });
});
