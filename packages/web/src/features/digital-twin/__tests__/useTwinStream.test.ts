/**
 * packages/web/src/features/digital-twin/__tests__/useTwinStream.test.ts
 *
 * Tests the useTwinStream hook in isolation by mocking TwinWSClient.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useTwinStream } from "../hooks/useTwinStream";

// ---------------------------------------------------------------------------
// Mock TwinWSClient
// ---------------------------------------------------------------------------

const mockConnect    = vi.fn();
const mockDisconnect = vi.fn();
// Default: send succeeds (returns true). Override per test when needed.
const mockSend       = vi.fn(() => true);
const mockRttMs      = vi.fn(() => null as number | null);

// Capture callbacks so tests can fire them manually
let capturedOpts: Record<string, (...args: unknown[]) => void> = {};

vi.mock("../../../lib/wsClient", () => ({
  TwinWSClient: vi.fn((opts: Record<string, unknown>) => {
    capturedOpts = opts as Record<string, (...args: unknown[]) => void>;
    return {
      connect:    mockConnect,
      disconnect: mockDisconnect,
      send:       mockSend,
      get rttMs() { return mockRttMs(); },
    };
  }),
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const PLANT_ID = "plant-test-123";

const WELCOME_MSG = {
  data: {
    plant_id:           PLANT_ID,
    org_id:             "org-test",
    server_time:        "2026-07-12T04:00:00Z",
    reconnect_token:    "tok",
    tick_interval_seconds: 5,
    initial_state: {
      operating_mode:   "running",
      current_actuals:  { co2_outlet_pct: 1.8, mesh_dp_mmH2O: 180 },
      current_setpoints: {},
      performance:      { co2_capture_pct: 87.0 },
      active_alerts:    [],
      uptime_seconds:   3600,
    },
  },
};

const TICK_MSG = {
  data: {
    operating_mode:   "running",
    current_actuals:  { co2_outlet_pct: 2.0, mesh_dp_mmH2O: 190 },
    current_setpoints: {},
    performance:      { co2_capture_pct: 85.0 },
    uptime_seconds:   3700,
  },
};

const ALERT_MSG = {
  data: {
    alert_id:    "alert-1",
    severity:    "HIGH" as const,
    title:       "High CO₂ outlet",
    message:     "Outlet exceeds 3%",
    triggered_at: "2026-07-12T04:01:00Z",
  },
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

// Helper: restore default implementations after reset
function restoreDefaults() {
  mockSend.mockImplementation(() => true);
  mockRttMs.mockImplementation(() => null);
}

describe("useTwinStream — initial state", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("starts with null twinState and disconnected", () => {
    const { result } = renderHook(() =>
      useTwinStream({ plantId: PLANT_ID, autoConnect: false }),
    );
    expect(result.current.twinState).toBeNull();
    expect(result.current.connectionState).toBe("disconnected");
  });

  it("auto-connects on mount when autoConnect=true", () => {
    renderHook(() => useTwinStream({ plantId: PLANT_ID, autoConnect: true }));
    expect(mockConnect).toHaveBeenCalledTimes(1);
  });

  it("does NOT connect when autoConnect=false", () => {
    renderHook(() => useTwinStream({ plantId: PLANT_ID, autoConnect: false }));
    expect(mockConnect).not.toHaveBeenCalled();
  });
});

describe("useTwinStream — welcome message", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("hydrates twinState from welcome.initial_state", async () => {
    const { result } = renderHook(() =>
      useTwinStream({ plantId: PLANT_ID }),
    );

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
    });

    expect(result.current.twinState).not.toBeNull();
    expect(result.current.twinState?.operating_mode).toBe("running");
    expect(result.current.twinState?.plant_id).toBe(PLANT_ID);
    expect(result.current.connectionState).toBe("connected");
  });
});

describe("useTwinStream — tick message", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("updates twinState on tick", () => {
    const { result } = renderHook(() => useTwinStream({ plantId: PLANT_ID }));

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
      capturedOpts.onTick?.(TICK_MSG);
    });

    expect(result.current.twinState?.uptime_seconds).toBe(3700);
    expect(result.current.twinState?.performance.co2_capture_pct).toBe(85.0);
  });
});

describe("useTwinStream — alerts", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("adds an alert to the map on onAlert", () => {
    const { result } = renderHook(() => useTwinStream({ plantId: PLANT_ID }));

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
      capturedOpts.onAlert?.(ALERT_MSG);
    });

    expect(result.current.alerts.size).toBe(1);
    expect(result.current.alerts.get("alert-1")?.severity).toBe("HIGH");
  });

  it("removes an alert from the map on onAlertCleared", () => {
    const { result } = renderHook(() => useTwinStream({ plantId: PLANT_ID }));

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
      capturedOpts.onAlert?.(ALERT_MSG);
      capturedOpts.onAlertCleared?.({ data: { alert_id: "alert-1" } });
    });

    expect(result.current.alerts.size).toBe(0);
  });

  it("calls onAlert callback prop when alert arrives", () => {
    const onAlert = vi.fn();
    renderHook(() => useTwinStream({ plantId: PLANT_ID, onAlert }));

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
      capturedOpts.onAlert?.(ALERT_MSG);
    });

    expect(onAlert).toHaveBeenCalledWith(ALERT_MSG.data);
  });
});

describe("useTwinStream — sendCommand", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("returns false when not connected", () => {
    // Override: make send return false for this test
    mockSend.mockImplementation(() => false);
    const { result } = renderHook(() =>
      useTwinStream({ plantId: PLANT_ID, autoConnect: false }),
    );
    const ok = result.current.sendCommand({ command: "start_equipment", target: "id_fan" });
    expect(ok).toBe(false);
  });

  it("returns true when WS send succeeds", () => {
    // mockSend default is () => true (restored in beforeEach)
    const { result } = renderHook(() => useTwinStream({ plantId: PLANT_ID }));
    act(() => { capturedOpts.onConnect?.(WELCOME_MSG); });

    let ok = false;
    act(() => {
      ok = result.current.sendCommand({ command: "start_equipment", target: "id_fan" });
    });

    expect(mockSend).toHaveBeenCalled();
    expect(ok).toBe(true);
  });
});

describe("useTwinStream — reconnect / disconnect", () => {
  beforeEach(() => { vi.resetAllMocks(); restoreDefaults(); capturedOpts = {}; });

  it("calls client.disconnect on hook unmount", () => {
    const { unmount } = renderHook(() => useTwinStream({ plantId: PLANT_ID }));
    unmount();
    expect(mockDisconnect).toHaveBeenCalled();
  });

  it("transitions to reconnecting on disconnect", () => {
    const { result } = renderHook(() =>
      useTwinStream({ plantId: PLANT_ID, maxReconnectAttempts: 5 }),
    );

    act(() => {
      capturedOpts.onConnect?.(WELCOME_MSG);
      capturedOpts.onDisconnect?.("network error");
    });

    expect(result.current.connectionState).toBe("reconnecting");
    expect(result.current.reconnectAttempt).toBe(1);
  });
});
