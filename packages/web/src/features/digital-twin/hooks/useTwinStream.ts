/**
 * packages/web/src/features/digital-twin/hooks/useTwinStream.ts
 *
 * React hook that wraps TwinWSClient with React state for the UI.
 *
 * Returns live TwinState, active alerts, connection status, and
 * imperative helpers (sendCommand, acknowledgeAlert, reconnect).
 */

import { useEffect, useRef, useCallback, useReducer } from "react";
import { TwinWSClient, TwinWSClientOptions } from "../../../lib/wsClient";
import {
  AlertData,
  TickData,
  WelcomeData,
  CommandData,
} from "../../../types/ws";
import { TwinState, ConnectionState } from "../types/twin";
import { useAuthStore } from "../../../store/authStore";

// ---------------------------------------------------------------------------
// State shape
// ---------------------------------------------------------------------------

interface StreamState {
  twinState: TwinState | null;
  alerts: Map<string, AlertData>;
  connectionState: ConnectionState;
  reconnectAttempt: number;
  rttMs: number | null;
  lastError: string | null;
  lastMessageAt: Date | null;
}

type StreamAction =
  | { type: "CONNECTED"; welcome: WelcomeData }
  | { type: "TICK"; tick: TickData }
  | { type: "ALERT_ADD"; alert: AlertData }
  | { type: "ALERT_REMOVE"; alertId: string }
  | { type: "DISCONNECTED"; reason: string }
  | { type: "CONNECTING" }
  | { type: "RECONNECTING"; attempt: number }
  | { type: "RTT"; ms: number }
  | { type: "ERROR"; message: string };

function reducer(state: StreamState, action: StreamAction): StreamState {
  switch (action.type) {
    case "CONNECTING":
      return { ...state, connectionState: "connecting", lastError: null };

    case "CONNECTED": {
      const wd = action.welcome;
      const raw = wd.initial_state as Record<string, unknown>;
      const twinState: TwinState = {
        plant_id:          wd.plant_id,
        org_id:            wd.org_id,
        operating_mode:    (raw.operating_mode as TwinState["operating_mode"]) ?? "idle",
        current_actuals:   (raw.current_actuals as TwinState["current_actuals"]) ?? {},
        current_setpoints: (raw.current_setpoints as TwinState["current_setpoints"]) ?? {},
        performance:       (raw.performance as TwinState["performance"]) ?? {},
        next_maintenance:  raw.next_maintenance as TwinState["next_maintenance"],
        active_alerts:     (raw.active_alerts as AlertData[]) ?? [],
        uptime_seconds:    (raw.uptime_seconds as number) ?? 0,
        last_update:       wd.server_time,
      };
      return { ...state, twinState, connectionState: "connected", reconnectAttempt: 0, lastMessageAt: new Date() };
    }

    case "TICK":
      if (!state.twinState) return state;
      return {
        ...state,
        twinState: {
          ...state.twinState,
          operating_mode:   action.tick.operating_mode,
          current_actuals:  action.tick.current_actuals,
          current_setpoints: action.tick.current_setpoints as TwinState["current_setpoints"],
          performance:      action.tick.performance,
          next_maintenance: action.tick.next_maintenance ?? null,
          uptime_seconds:   action.tick.uptime_seconds,
          last_update:      new Date().toISOString(),
        },
        lastMessageAt: new Date(),
      };

    case "ALERT_ADD": {
      const next = new Map(state.alerts);
      next.set(action.alert.alert_id, action.alert);
      return { ...state, alerts: next };
    }

    case "ALERT_REMOVE": {
      const next = new Map(state.alerts);
      next.delete(action.alertId);
      return { ...state, alerts: next };
    }

    case "DISCONNECTED":
      return { ...state, connectionState: "disconnected" };

    case "RECONNECTING":
      return { ...state, connectionState: "reconnecting", reconnectAttempt: action.attempt };

    case "RTT":
      return { ...state, rttMs: action.ms };

    case "ERROR":
      return { ...state, lastError: action.message };

    default:
      return state;
  }
}

const initial: StreamState = {
  twinState:       null,
  alerts:          new Map(),
  connectionState: "disconnected",
  reconnectAttempt: 0,
  rttMs:           null,
  lastError:       null,
  lastMessageAt:   null,
};

// ---------------------------------------------------------------------------
// Hook options
// ---------------------------------------------------------------------------

export interface UseTwinStreamOptions {
  plantId: string;
  baseUrl?: string;
  getToken?: () => string | null;
  tickIntervalSeconds?: number;
  maxReconnectAttempts?: number;
  autoConnect?: boolean;
  onAlert?: (alert: AlertData) => void;
  onAlertCleared?: (alertId: string) => void;
}

export interface UseTwinStreamReturn {
  twinState:        TwinState | null;
  alerts:           Map<string, AlertData>;
  connectionState:  ConnectionState;
  reconnectAttempt: number;
  rttMs:            number | null;
  lastError:        string | null;
  lastMessageAt:    Date | null;
  isConnected:      boolean;
  sendCommand:      (cmd: CommandData) => boolean;
  acknowledgeAlert: (alertId: string) => void;
  reconnect:        () => void;
  disconnect:       () => void;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useTwinStream(opts: UseTwinStreamOptions): UseTwinStreamReturn {
  const {
    plantId,
    baseUrl = window.location.origin,
    getToken = () => useAuthStore.getState().accessToken,
    tickIntervalSeconds = 5,
    maxReconnectAttempts = 10,
    autoConnect = true,
    onAlert,
    onAlertCleared,
  } = opts;

  const [state, dispatch] = useReducer(reducer, initial);
  const clientRef = useRef<TwinWSClient | null>(null);
  const reconnectAttemptRef = useRef(0);

  // Build + (re)connect the client
  const connect = useCallback(() => {
    clientRef.current?.disconnect();

    dispatch({ type: "CONNECTING" });

    const clientOpts: TwinWSClientOptions = {
      baseUrl,
      plantId,
      getToken,
      tickIntervalSeconds,
      maxReconnectAttempts,

      onConnect: (msg) => {
        dispatch({ type: "CONNECTED", welcome: msg.data });
      },

      onTick: (msg) => {
        dispatch({ type: "TICK", tick: msg.data });
      },

      onAlert: (msg) => {
        dispatch({ type: "ALERT_ADD", alert: msg.data });
        onAlert?.(msg.data);
      },

      onAlertCleared: (msg) => {
        dispatch({ type: "ALERT_REMOVE", alertId: msg.data.alert_id });
        onAlertCleared?.(msg.data.alert_id);
      },

      onDisconnect: (reason) => {
        reconnectAttemptRef.current += 1;
        if (reconnectAttemptRef.current <= maxReconnectAttempts) {
          dispatch({ type: "RECONNECTING", attempt: reconnectAttemptRef.current });
        } else {
          dispatch({ type: "DISCONNECTED", reason });
        }
      },

      onError: (err) => {
        const message = err instanceof Error ? err.message : String(err);
        dispatch({ type: "ERROR", message });
      },
    };

    const client = new TwinWSClient(clientOpts);
    clientRef.current = client;
    client.connect();
  }, [plantId, baseUrl, getToken, tickIntervalSeconds, maxReconnectAttempts, onAlert, onAlertCleared]);

  // Auto-connect on mount; clean up on unmount
  useEffect(() => {
    if (autoConnect) connect();
    return () => {
      clientRef.current?.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // RTT polling
  useEffect(() => {
    if (state.connectionState !== "connected") return;
    const rttHandle = setInterval(() => {
      const rtt = clientRef.current?.rttMs;
      if (rtt != null) dispatch({ type: "RTT", ms: rtt });
    }, 5000);
    return () => clearInterval(rttHandle);
  }, [state.connectionState]);

  const sendCommand = useCallback((cmd: CommandData): boolean => {
    if (!clientRef.current) return false;
    return clientRef.current.send({
      type: "command",
      version: "1.0",
      id: crypto.randomUUID(),
      ts: new Date().toISOString(),
      seq: 0,
      data: cmd,
    });
  }, []);

  const acknowledgeAlert = useCallback((alertId: string) => {
    sendCommand({ command: "acknowledge_alert", alert_id: alertId });
  }, [sendCommand]);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
    dispatch({ type: "DISCONNECTED", reason: "manual" });
  }, []);

  return {
    twinState:        state.twinState,
    alerts:           state.alerts,
    connectionState:  state.connectionState,
    reconnectAttempt: state.reconnectAttempt,
    rttMs:            state.rttMs,
    lastError:        state.lastError,
    lastMessageAt:    state.lastMessageAt,
    isConnected:      state.connectionState === "connected",
    sendCommand,
    acknowledgeAlert,
    reconnect:        connect,
    disconnect,
  };
}
