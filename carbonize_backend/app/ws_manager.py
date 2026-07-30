"""
Production WebSocket Manager with Backpressure
Fixes Bottleneck B18: Connection storms
"""

import asyncio
import time
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger("ws-manager")


@dataclass
class ConnectionPolicy:
    """Client connection policy."""
    max_connections_per_ip: int = 5
    max_total_connections: int = 1000
    max_messages_per_sec: int = 60
    max_queue_size: int = 100
    idle_timeout_sec: float = 300.0
    connect_rate_per_sec: int = 10


@dataclass
class ClientState:
    """Per-client state."""
    websocket: WebSocket
    ip: str
    connected_at: float
    message_count: int = 0
    last_message_at: float = 0.0
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=100))
    drop_count: int = 0
    
    @property
    def rate_limit_exceeded(self) -> bool:
        if self.message_count == 0:
            return False
        elapsed = time.time() - self.connected_at
        return (self.message_count / max(elapsed, 0.001)) > 60


class WebSocketManager:
    """Backpressure-aware WebSocket manager."""
    
    def __init__(self, policy: Optional[ConnectionPolicy] = None):
        self.policy = policy or ConnectionPolicy()
        self._clients: Dict[str, ClientState] = {}
        self._connections_by_ip: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
        
        # ─── Token bucket for connection rate limiting ─────────────
        self._connect_tokens = self.policy.connect_rate_per_sec
        self._last_token_refill = time.time()
    
    async def connect(self, websocket: WebSocket, ip: str) -> Optional[ClientState]:
        """Accept new connection with rate limiting."""
        # ─── Rate limit: token bucket ───────────────────────────────
        if not self._acquire_connect_token():
            await websocket.close(code=1008, reason="Connection rate exceeded")
            logger.warning(f"Connection rate exceeded for {ip}")
            return None
        
        # ─── Per-IP limit ───────────────────────────────────────────
        ip_count = len(self._connections_by_ip[ip])
        if ip_count >= self.policy.max_connections_per_ip:
            await websocket.close(code=1008, reason="Too many connections from your IP")
            return None
        
        # ─── Total limit ────────────────────────────────────────────
        async with self._lock:
            if len(self._clients) >= self.policy.max_total_connections:
                await websocket.close(code=1013, reason="Server at capacity")
                return None
            
            await websocket.accept()
            
            client_id = f"{ip}:{id(websocket)}"
            state = ClientState(
                websocket=websocket,
                ip=ip,
                connected_at=time.time()
            )
            
            self._clients[client_id] = state
            self._connections_by_ip[ip].add(client_id)
            
            logger.info(f"Connected: {client_id} (total: {len(self._clients)})")
            return state
    
    async def disconnect(self, client_id: str) -> None:
        """Clean up connection."""
        async with self._lock:
            if client_id in self._clients:
                state = self._clients[client_id]
                self._connections_by_ip[state.ip].discard(client_id)
                if not self._connections_by_ip[state.ip]:
                    del self._connections_by_ip[state.ip]
                del self._clients[client_id]
                logger.info(f"Disconnected: {client_id} (remaining: {len(self._clients)})")
    
    async def send_to_client(self, client_id: str, message: dict) -> bool:
        """Send with backpressure — drop if queue full."""
        if client_id not in self._clients:
            return False
        
        state = self._clients[client_id]
        try:
            state.queue.put_nowait(message)
            return True
        except asyncio.QueueFull:
            state.drop_count += 1
            if state.drop_count % 100 == 0:
                logger.warning(f"Client {client_id} dropped {state.drop_count} messages")
            return False
    
    async def broadcast(self, message: dict, filter_ip: Optional[str] = None) -> int:
        """Broadcast to all clients with backpressure."""
        sent = 0
        for client_id in list(self._clients.keys()):
            state = self._clients[client_id]
            if filter_ip and state.ip == filter_ip:
                continue
            if await self.send_to_client(client_id, message):
                sent += 1
        return sent
    
    def _acquire_connect_token(self) -> bool:
        """Token-bucket rate limiter for new connections."""
        now = time.time()
        elapsed = now - self._last_token_refill
        refill = int(elapsed * self.policy.connect_rate_per_sec)
        if refill > 0:
            self._connect_tokens = min(
                self.policy.connect_rate_per_sec,
                self._connect_tokens + refill
            )
            self._last_token_refill = now
        
        if self._connect_tokens > 0:
            self._connect_tokens -= 1
            return True
        return False
    
    def get_stats(self) -> dict:
        """Return connection statistics."""
        return {
            "total_connections": len(self._clients),
            "by_ip": {ip: len(s) for ip, s in self._connections_by_ip.items()},
            "total_drops": sum(c.drop_count for c in self._clients.values()),
            "avg_messages_per_client": (
                sum(c.message_count for c in self._clients.values()) /
                max(len(self._clients), 1)
            )
        }


# Singleton
ws_manager = WebSocketManager()
