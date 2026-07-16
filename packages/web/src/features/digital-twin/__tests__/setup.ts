/**
 * packages/web/src/features/digital-twin/__tests__/setup.ts
 *
 * Vitest global test setup for React Testing Library.
 */
import "@testing-library/jest-dom";

// ---------------------------------------------------------------------------
// Browser API polyfills for jsdom
// ---------------------------------------------------------------------------

// ResizeObserver — required by Recharts' <ResponsiveContainer>
if (typeof ResizeObserver === "undefined") {
  global.ResizeObserver = class ResizeObserver {
    observe()   { /* noop */ }
    unobserve() { /* noop */ }
    disconnect(){ /* noop */ }
  };
}

// matchMedia — required by Recharts responsive hooks
if (typeof window.matchMedia === "undefined") {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener:    () => {},
      removeListener: () => {},
      addEventListener:    () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
}

// IntersectionObserver — future-proofing
if (typeof IntersectionObserver === "undefined") {
  global.IntersectionObserver = class IntersectionObserver {
    observe()   { /* noop */ }
    unobserve() { /* noop */ }
    disconnect(){ /* noop */ }
    takeRecords() { return []; }
    readonly root = null;
    readonly rootMargin = "";
    readonly thresholds = [];
  };
}

