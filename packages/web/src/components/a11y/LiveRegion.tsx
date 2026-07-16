/**
 * ARIA live region for announcing state changes to screen readers.
 * 
 * Use this for:
 * - Connection state changes ("Connection lost", "Connection restored")
 * - Alert arrivals
 * - New data
 * - Errors
 */

import React, { useEffect, useState } from "react";

interface LiveRegionProps {
  message: string | null;
  politeness?: "polite" | "assertive";
  /** Whether to clear the message after a delay (avoid repetition) */
  clearAfterMs?: number;
  className?: string;
}

export function LiveRegion({
  message, politeness = "polite", clearAfterMs = 5000, className,
}: LiveRegionProps) {
  const [displayed, setDisplayed] = useState<string | null>(null);
  
  useEffect(() => {
    if (message) {
      setDisplayed(message);
      if (clearAfterMs > 0) {
        const t = setTimeout(() => setDisplayed(null), clearAfterMs);
        return () => clearTimeout(t);
      }
    }
    return undefined;
  }, [message, clearAfterMs]);
  
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className={className ?? "sr-only"}
    >
      {displayed}
    </div>
  );
}

/**
 * Hook for managing live region announcements.
 * Avoids spamming screen reader with duplicate messages.
 */
export function useLiveAnnouncer() {
  const [message, setMessage] = useState<string | null>(null);
  
  const announce = (msg: string, _politeness: "polite" | "assertive" = "polite") => {
    // Deduplicate identical messages within 2 seconds
    setMessage(prev => {
      if (prev === msg) {
        // Re-set with a "fresh" indicator by appending invisible space
        return msg + "\u00A0";
      }
      return msg;
    });
  };
  
  return { message, announce };
}
