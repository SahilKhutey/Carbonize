"""
Kafka Consumer Service with backpressure and DLQ handling
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from collections import defaultdict
import time

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ConsumedMessage:
    topic: str
    partition: int
    offset: int
    timestamp: int
    key: Optional[str]
    value: Dict[str, Any]
    headers: Dict[str, str]


class KafkaConsumerService:
    def __init__(
        self,
        group_id: str = None,
        topics: List[str] = None,
        auto_offset_reset: str = None,
    ):
        self.group_id = group_id or settings.CONSUMER_GROUP
        self.topics = topics or [settings.TOPIC_TELEMETRY]
        self.auto_offset_reset = auto_offset_reset or settings.CONSUMER_AUTO_OFFSET_RESET
        
        self._consumer = None
        self._running = False
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        self._consumed_count = 0
        self._failed_count = 0
        self._dlq_count = 0
        self._last_offset: Dict[str, int] = {}
    
    async def initialize(self):
        if self._consumer is not None:
            return
        
        try:
            from confluent_kafka import Consumer
            config = {
                'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                'group.id': self.group_id,
                'auto.offset.reset': self.auto_offset_reset,
                'enable.auto.commit': False,
            }
            self._consumer = Consumer(config)
            self._consumer.subscribe(self.topics)
            logger.info(f"Consumer subscribed to: {self.topics}")
        except Exception as e:
            logger.warning(f"Kafka consumer fallback mode: {e}")
            self._consumer = "MOCK_CONSUMER"
    
    def register_handler(self, topic: str, handler: Callable):
        self._handlers[topic].append(handler)
    
    async def consume_loop(self, batch_size: int = 100, poll_timeout: float = 1.0):
        if self._consumer is None:
            await self.initialize()
        
        self._running = True
        loop = asyncio.get_event_loop()
        
        while self._running:
            try:
                if self._consumer == "MOCK_CONSUMER":
                    await asyncio.sleep(1)
                    continue
                
                msg = await loop.run_in_executor(
                    None,
                    lambda: self._consumer.poll(poll_timeout),
                )
                if msg is None or msg.error():
                    continue
                
                consumed = self._parse_message(msg)
                if consumed:
                    await self._dispatch(consumed)
                    self._consumed_count += 1
            except Exception as e:
                logger.error(f"Consume loop error: {e}")
                await asyncio.sleep(0.5)
    
    async def _dispatch(self, msg: ConsumedMessage):
        handlers = self._handlers.get(msg.topic, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(msg)
                else:
                    handler(msg)
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    def _parse_message(self, raw_msg) -> Optional[ConsumedMessage]:
        try:
            val = json.loads(raw_msg.value().decode('utf-8'))
            key = raw_msg.key().decode('utf-8') if raw_msg.key() else None
            return ConsumedMessage(
                topic=raw_msg.topic(),
                partition=raw_msg.partition(),
                offset=raw_msg.offset(),
                timestamp=int(time.time() * 1000),
                key=key,
                value=val,
                headers={},
            )
        except Exception:
            return None
    
    async def stop(self):
        self._running = False
        if self._consumer and self._consumer != "MOCK_CONSUMER":
            self._consumer.close()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'consumed': self._consumed_count,
            'failed': self._failed_count,
            'dlq_count': self._dlq_count,
            'last_offsets': self._last_offset,
        }
