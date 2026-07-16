/**
 * Accessible label/description for screen readers.
 * 
 * Use this for:
 * - Labels on icon-only buttons
 * - Description text for complex UI (charts, etc.)
 * - Status announcements (live regions)
 */

import React from "react";

interface VisuallyHiddenProps {
  children: React.ReactNode;
  /** Render as a specific element (default: span) */
  as?: "span" | "div" | "p" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
  /** ARIA live region politeness */
  live?: "off" | "polite" | "assertive";
  /** ARIA role */
  role?: string;
}

export function VisuallyHidden({
  children, as: Component = "span", live, role,
}: VisuallyHiddenProps) {
  const ariaProps: Record<string, string> = {};
  if (live) ariaProps["aria-live"] = live;
  if (role) ariaProps["role"] = role;
  
  return (
    <Component className="sr-only" {...ariaProps}>
      {children}
    </Component>
  );
}
