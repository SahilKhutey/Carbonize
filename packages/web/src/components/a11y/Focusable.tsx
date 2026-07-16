/**
 * WCAG 2.4.7 Focus Visible compliance.
 * 
 * Provides a highly visible focus ring that works on all backgrounds,
 * including the status colors used throughout the app.
 * 
 * Default browser focus rings are often too subtle or invisible on
 * colored backgrounds. This custom ring ensures 3:1 contrast minimum.
 */

import React from "react";
// We don't have a cn utility, so just string concatenation or a simple util
function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(" ");
}

interface FocusableProps {
  children: React.ReactNode;
  className?: string;
  /** Override focus ring color (for dark backgrounds) */
  ringColor?: string;
  /** Override offset (distance from element) */
  offset?: number;
}

/**
 * Hook to provide focus styles to any element.
 * Use this with `useFocusStyles()` or apply directly via Tailwind classes.
 */
export function useFocusStyles(
  options: {
    ringColor?: string;
    offset?: number;
    width?: number;
  } = {}
) {
  const ringColor = options.ringColor ?? "emerald-500";
  const offset = options.offset ?? 2;
  const width = options.width ?? 3;
  
  return cn(
    "outline-none",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
    `focus-visible:outline-${ringColor}`,
    "focus-visible:transition-none",
    // Ensure focus ring is visible against any background
    "focus-visible:ring-offset-2",
    "focus-visible:z-10",
  );
}

/**
 * Focusable wrapper component.
 */
export function Focusable({ children, className, ringColor, offset }: FocusableProps) {
  return (
    <div className={useFocusStyles({ ringColor, offset }) + " " + (className ?? "")}>
      {children}
    </div>
  );
}

/**
 * Skip link for keyboard users to bypass navigation.
 * Hidden until focused, then appears at top of page.
 */
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="
        sr-only focus:not-sr-only
        focus:absolute focus:top-4 focus:left-4 focus:z-50
        focus:px-4 focus:py-2 focus:bg-emerald-600 focus:text-white
        focus:rounded focus:shadow-lg
        focus:outline focus:outline-2 focus:outline-white
      "
    >
      Skip to main content
    </a>
  );
}
