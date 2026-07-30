"""Production Redis Client with Streams + Replay."""

import redis.asyncio as redis
import json
from datetime import datetime
from typing import AsyncIterator, Optional
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
TELEMETRY_STREAM = "carbonize:telemetry"
STREAM_MAX_LEN = 100_000   # ~6 hours @ 5Hz
REPLAY_BATCH = 100


class TelemetryStream:
    """Async Redis Streams wrapper."""
    
    def __init__(self, url: str = REDIS_URL):
        self.url = url
        self._pool: Optional[redis.ConnectionPool] = None
    
    async def get_redis(self) -> redis.Redis:
        if not self._pool:
            self._pool = redis.ConnectionPool.from_url(self.url, max_connections=50)
        return redis.Redis(connection_pool=self._pool)
    
    async def publish(self, robot_id: str, payload: dict) -> str:
        """Publish telemetry to stream; return entry ID."""
        r = await self.get_redis()
        entry_id = await r.xadd(
            TELEMETRY_STREAM,
            {
                "robot_id": robot_id,
                "ts": datetime.utcnow().isoformat(),
                "data": json.dumps(payload)
            },
            maxlen=STREAM_MAX_LEN,
            approximate=True
        )
        return entry_id.decode() if isinstance(entry_id, bytes) else entry_id
    
    async def replay(self, start_id: str = "-", 
                     count: int = REPLAY_BATCH,
                     block_ms: int = 1000) -> AsyncIterator[dict]:
        """Replay telemetry from given ID; supports live tail."""
        r = await self.get_redis()
        last_id = start_id
        while True:
            result = await r.xread({TELEMETRY_STREAM: last_id}, 
                                   count=count, block=block_ms)
            if not result:
                yield {"type": "heartbeat"}
                continue
            for _stream, entries in result:
                for entry_id, fields in entries:
                    last_id = entry_id
                    yield {
                        "type": "entry",
                        "id": entry_id.decode() if isinstance(entry_id, bytes) else entry_id,
                        "robot_id": fields.get(b"robot_id", b"").decode(),
                        "ts": fields.get(b"ts", b"").decode(),
                        "data": json.loads(fields.get(b"data", b"{}").decode())
                    }
    
    async def realtime(self, robot_id: str) -> AsyncIterator[dict]:
        """Live tail of telemetry for a specific robot."""
        r = await self.get_redis()
        pubsub = r.pubsub()
        channel = f"alerts:{robot_id}"
        await pubsub.subscribe(channel)
        try:
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    data = msg["data"]
                    if isinstance(data, bytes):
                        data = data.decode()
                    yield {"type": "alert", "data": json.loads(data)}
        finally:
            await pubsub.unsubscribe(channel)


# Singleton
_telemetry_stream = None

async def get_telemetry_stream() -> TelemetryStream:
    global _telemetry_stream
    if not _telemetry_stream:
        _telemetry_stream = TelemetryStream()
    return _telemetry_stream

async def get_redis():
    stream = await get_telemetry_stream()
    return await stream.get_redis()
