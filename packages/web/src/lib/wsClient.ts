/**
 * packages/web/src/lib/wsClient.ts
 *
 * Type-safe WebSocket client for the CBMS-Sim digital twin real-time stream.
 *
 * Features:
 *  - Exponential backoff reconnection with jitter (0s, 1s, 2s, 4s … 30s cap)
 *  - Session resumption via reconnect_token + from_seq
 *  - RTT tracking (ping/pong round-trip)
 *  - Typed callbacks per server message type
 *  - Graceful disconnect (sends close frame)
 */

import {
  PROTOCOL_SUBPROTOCOL,
  PROTOCOL_VERSION,
  WSMessage,
  WelcomeMessage,
  TickMessage,
  AlertMessage,
  AlertClearedMessage,
  CommandAckMessage,
  ErrorMessage,
  GoodbyeMessage,
  ClientMessage,
  CommandData,
  isWelcome,
  isTick,
  isAlert,
  isAlertCleared,
  isCommandAck,
  isPong,
  isError,
  isGoodbye,
} from "@/types/ws";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

export interface TwinWSClientOptions {
  /** Base URL of the API, e.g. https://api.cbms.in  */
  baseUrl: string;
  /** Plant UUID to stream */
  plantId: string;
  /** Callback to retrieve a fresh JWT access token */
  getToken: () => string | null;

  // Event callbacks
  onConnect?: (msg: WelcomeMessage) => void;
  onTick?: (msg: TickMessage) => void;
  onAlert?: (msg: AlertMessage) => void;
  onAlertCleared?: (msg: AlertClearedMessage) => void;
  onCommandAck?: (msg: CommandAckMessage) => void;
  onError?: (msg: ErrorMessage | Error) => void;
  onGoodbye?: (msg: GoodbyeMessage) => void;
  onDisconnect?: (reason: string) => void;

  /** Desired tick interval in seconds (1–60). Default: 5 */
  tickIntervalSeconds?: number;
  /** Max reconnect attempts before giving up. Default: 10 */
  maxReconnectAttempts?: number;
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class TwinWSClient {
  private ws: WebSocket | null = null;
  private reconnectAttempt = 0;
  private lastSeq = 0;
  private reconnectToken: string | null = null;
  private manualDisconnect = false;

  // RTT state
  private lastPingSentAt: number | null = null;
  private lastRttMs: number | null = null;

  // Heartbeat (client-side, 30 s)
  private heartbeatHandle: ReturnType<typeof setInterval> | null = null;

  constructor(private readonly opts: TwinWSClientOptions) {}

  /** Open the WebSocket connection. */
  connect(): void {
    this.manualDisconnect = false;
    this.openSocket();
  }

  /** Close the connection gracefully. */
  disconnect(): void {
    this.manualDisconnect = true;
    this.stopHeartbeat();
    this.ws?.close(1000, "Client disconnect");
  }

  /** Send a typed client message. Returns false if socket is not open. */
  send(message: ClientMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  /** Send a setpoint command. */
  setSetpoint(target: string, value: number, reason?: string): boolean {
    return this.send(this.makeClientMessage("command", {
      command: "set_setpoint",
      target,
      value,
      reason,
    } satisfies CommandData));
  }

  /** Send a manual ping and record the timestamp for RTT calculation. */
  ping(): boolean {
    this.lastPingSentAt = Date.now();
    return this.send(this.makeClientMessage("ping", {
      client_ts: new Date().toISOString(),
    }));
  }

  get rttMs(): number | null { return this.lastRttMs; }

  // ------------------------------------------------------------------
  // Private — socket lifecycle
  // ------------------------------------------------------------------

  private openSocket(): void {
    const token = this.opts.getToken();
    if (!token) {
      this.opts.onError?.(new Error("No auth token available"));
      return;
    }

    // Build wss:// URL
    const base = this.opts.baseUrl.replace(/^http/, "ws");
    const url = new URL(`${base}/api/v1/twin/${this.opts.plantId}/stream`);
    url.searchParams.set("token", token);

    this.ws = new WebSocket(url.toString(), [PROTOCOL_SUBPROTOCOL]);

    this.ws.onopen = () => {
      this.reconnectAttempt = 0;

      // Send subscribe (carries resume info if reconnecting)
      this.send(this.makeClientMessage("subscribe", {
        tick_interval_seconds: this.opts.tickIntervalSeconds ?? 5,
        include_alerts: true,
        include_predictions: true,
        resume_from_seq: this.lastSeq > 0 ? this.lastSeq : undefined,
        reconnect_token: this.reconnectToken ?? undefined,
      }));

      this.startHeartbeat();
    };

    this.ws.onmessage = (evt: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(evt.data) as WSMessage;
        this.handleMessage(msg);
      } catch (err) {
        this.opts.onError?.(err instanceof Error ? err : new Error(String(err)));
      }
    };

    this.ws.onclose = (evt: CloseEvent) => {
      this.stopHeartbeat();
      const reason = evt.reason || `code ${evt.code}`;
      this.opts.onDisconnect?.(reason);
      if (!this.manualDisconnect) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      this.opts.onError?.(new Error("WebSocket transport error"));
    };
  }

  // ------------------------------------------------------------------
  // Private — message dispatch
  // ------------------------------------------------------------------

  private handleMessage(msg: WSMessage): void {
    this.lastSeq = msg.seq;

    if (isWelcome(msg)) {
      this.reconnectToken = msg.data.reconnect_token;
      this.opts.onConnect?.(msg);
    } else if (isTick(msg)) {
      this.opts.onTick?.(msg);
    } else if (isAlert(msg)) {
      this.opts.onAlert?.(msg);
    } else if (isAlertCleared(msg)) {
      this.opts.onAlertCleared?.(msg);
    } else if (isCommandAck(msg)) {
      this.opts.onCommandAck?.(msg);
    } else if (isPong(msg)) {
      if (this.lastPingSentAt !== null) {
        this.lastRttMs = Date.now() - this.lastPingSentAt;
        this.lastPingSentAt = null;
      }
    } else if (isError(msg)) {
      this.opts.onError?.(msg);
    } else if (isGoodbye(msg)) {
      this.opts.onGoodbye?.(msg);
    }
    // Unknown types are silently ignored — forward-compatible
  }

  // ------------------------------------------------------------------
  // Private — reconnection
  // ------------------------------------------------------------------

  private scheduleReconnect(): void {
    const max = this.opts.maxReconnectAttempts ?? 10;
    if (this.reconnectAttempt >= max) {
      this.opts.onError?.(new Error(`Reconnect failed after ${max} attempts`));
      return;
    }

    // Exponential backoff: 0s, 1s, 2s, 4s, 8s, 16s, 30s cap
    const base = this.reconnectAttempt === 0
      ? 0
      : Math.min(Math.pow(2, this.reconnectAttempt - 1) * 1000, 30_000);
    const jitter = Math.random() * 1000;
    const delay = base + jitter;

    this.reconnectAttempt++;
    setTimeout(() => { this.openSocket(); }, delay);
  }

  // ------------------------------------------------------------------
  // Private — heartbeat
  // ------------------------------------------------------------------

  private startHeartbeat(): void {
    this.heartbeatHandle = setInterval(() => { this.ping(); }, 30_000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatHandle !== null) {
      clearInterval(this.heartbeatHandle);
      this.heartbeatHandle = null;
    }
  }

  // ------------------------------------------------------------------
  // Private — helpers
  // ------------------------------------------------------------------

  private makeClientMessage<T extends string, D>(type: T, data: D): ClientMessage {
    return {
      type,
      version: PROTOCOL_VERSION,
      id: crypto.randomUUID(),
      ts: new Date().toISOString(),
      seq: 0, // server ignores client seq for now
      data,
    } as unknown as ClientMessage;
  }
}
