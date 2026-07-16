/**
 * Enhanced useWebSocket hook with:
 * - Connection state tracking
 * - Last update timestamp
 * - Stale detection
 * - Reconnection with backoff
 */

import { useEffect, useRef, useState, useCallback } from "react";

export type ConnectionState = 
  | "disconnected" | "connecting" | "connected" | "reconnecting" | "error";

export interface UseWebSocketOptions {
  url: string;
  token?: string;
  protocols?: string[];
  onMessage?: (msg: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (err: Event) => void;
  maxReconnectAttempts?: number;
  autoConnect?: boolean;
  pingIntervalMs?: number;
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    url, token, protocols = [],
    onMessage, onOpen, onClose, onError,
    maxReconnectAttempts = 10,
    autoConnect = true,
    pingIntervalMs = 25000,
  } = options;
  
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [lastConnectedAt, setLastConnectedAt] = useState<Date | null>(null);
  const [lastMessageAt, setLastMessageAt] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const intentionalCloseRef = useRef(false);
  
  const connect = useCallback(() => {
    // Note: token might be optional depending on your setup. 
    // If strict token is needed, check here.
    
    setConnectionState("connecting");
    setError(null);
    
    try {
      // Append token to URL if provided for this mock
      const finalUrl = token ? `${url}?token=${token}` : url;
      const ws = new WebSocket(finalUrl, protocols);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setConnectionState("connected");
        setIsConnected(true);
        setReconnectAttempt(0);
        setLastConnectedAt(new Date());
        onOpen?.();
        
        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, pingIntervalMs);
      };
      
      ws.onmessage = (event) => {
        setLastMessageAt(new Date());
        try {
          const msg = JSON.parse(event.data);
          onMessage?.(msg);
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };
      
      ws.onerror = (e) => {
        setError("WebSocket error");
        onError?.(e);
      };
      
      ws.onclose = (e) => {
        setIsConnected(false);
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }
        onClose?.();
        
        if (intentionalCloseRef.current) {
          // We initiated the close
          intentionalCloseRef.current = false;
          setConnectionState("disconnected");
          return;
        }
        
        // Unexpected close: try to reconnect
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        
        if (reconnectAttempt < maxReconnectAttempts) {
          setConnectionState("reconnecting");
          setReconnectAttempt(prev => prev + 1);
          
          // Exponential backoff with jitter
          const delay = Math.min(
            Math.pow(2, reconnectAttempt) * 1000,
            30000
          ) + Math.random() * 1000;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          setConnectionState("error");
          setError("Max reconnect attempts reached");
        }
      };
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed");
      setConnectionState("error");
    }
  }, [url, token, protocols.join(","), onMessage, onOpen, onClose, onError, maxReconnectAttempts, pingIntervalMs, reconnectAttempt]);
  
  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnectionState("disconnected");
    setIsConnected(false);
  }, []);
  
  const reconnect = useCallback(() => {
    setReconnectAttempt(0);
    if (wsRef.current) {
      intentionalCloseRef.current = true;
      wsRef.current.close();
    }
    setTimeout(() => connect(), 100);
  }, [connect]);
  
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect, autoConnect]);
  
  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === "string" ? data : JSON.stringify(data));
    } else {
      console.warn("WebSocket not connected; message dropped");
    }
  }, []);
  
  return {
    connectionState,
    isConnected,
    reconnectAttempt,
    lastMessageAt,
    lastConnectedAt,
    reconnect,
    disconnect,
    send,
    error,
  };
}
