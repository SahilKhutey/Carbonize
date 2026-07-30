"""
High-performance WebSocket fan-out service
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import time

from fastapi import WebSocket

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    robot_id: Optional[str] = None
    metric_types: Set[str] = field(default_factory=set)
    classes: Set[str] = field(default_factory=set)
    min_severity: str = 'info'
    model_version: Optional[str] = None
    bounding_box: Optional[Dict[str, float]] = None


@dataclass
class ClientState:
    websocket: WebSocket
    client_id: str
    connected_at: float
    subscription: Subscription = field(default_factory=Subscription)
    last_message_at: float = 0.0
    messages_sent: int = 0
    bytes_sent: int = 0
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=100))
    drop_count: int = 0
    user_id: Optional[str] = None


class WebSocketFanoutManager:
    SEVERITY_LEVELS = {'info': 0, 'warning': 1, 'error': 2, 'critical': 3}
    
    def __init__(self):
        self._clients: Dict[str, ClientState] = {}
        self._lock = asyncio.Lock()
        self._all_clients: Set[str] = set()
        
        self._messages_routed = 0
        self._bytes_routed = 0
        self._messages_dropped = 0
    
    async def add_client(self, websocket: WebSocket, client_id: str, user_id: Optional[str] = None) -> ClientState:
        async with self._lock:
            state = ClientState(
                websocket=websocket,
                client_id=client_id,
                connected_at=time.time(),
                user_id=user_id,
                last_message_at=time.time(),
            )
            self._clients[client_id] = state
            self._all_clients.add(client_id)
            asyncio.create_task(self._sender_task(state))
            logger.info(f"Client connected: {client_id} (total: {len(self._clients)})")
            return state
    
    async def remove_client(self, client_id: str):
        async with self._lock:
            if client_id in self._clients:
                self._all_clients.discard(client_id)
                del self._clients[client_id]
                logger.info(f"Client disconnected: {client_id}")
    
    async def update_subscription(self, client_id: str, subscription: Subscription):
        async with self._lock:
            if client_id in self._clients:
                self._clients[client_id].subscription = subscription
    
    async def broadcast_event(self, event_type: str, event: Dict[str, Any]):
        if not self._clients:
            return
        
        message = {
            'type': event_type,
            'data': event,
            'timestamp': int(time.time() * 1000),
        }
        message_bytes = json.dumps(message, default=str).encode('utf-8')
        
        for client_id in list(self._all_clients):
            state = self._clients.get(client_id)
            if state:
                try:
                    state.queue.put_nowait(message_bytes)
                    self._messages_routed += 1
                    self._bytes_routed += len(message_bytes)
                except asyncio.QueueFull:
                    state.drop_count += 1
                    self._messages_dropped += 1
    
    async def _sender_task(self, state: ClientState):
        try:
            while True:
                try:
                    message_bytes = await asyncio.wait_for(
                        state.queue.get(),
                        timeout=settings.WS_HEARTBEAT_INTERVAL,
                    )
                    await state.websocket.send_bytes(message_bytes)
                    state.messages_sent += 1
                    state.bytes_sent += len(message_bytes)
                    state.last_message_at = time.time()
                except asyncio.TimeoutError:
                    await state.websocket.send_json({
                        'type': 'heartbeat',
                        'timestamp': int(time.time() * 1000),
                    })
                except Exception:
                    break
        finally:
            await self.remove_client(state.client_id)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'connected_clients': len(self._clients),
            'messages_routed': self._messages_routed,
            'bytes_routed': self._bytes_routed,
            'messages_dropped': self._messages_dropped,
        }


fanout_manager = WebSocketFanoutManager()
