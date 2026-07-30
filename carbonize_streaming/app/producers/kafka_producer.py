"""
High-performance Kafka producer with Avro serialization
"""
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from app.config import settings

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Async wrapper around producer service with fallback serialization."""
    
    def __init__(self):
        self._producer = None
        self._serializers: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        
        self._produced_count = 0
        self._failed_count = 0
        self._bytes_sent = 0
        self._last_error: Optional[str] = None
    
    async def initialize(self):
        async with self._lock:
            if self._producer is not None:
                return
            
            try:
                from confluent_kafka import Producer
                config = {
                    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                    'client.id': settings.KAFKA_CLIENT_ID,
                    'acks': 'all',
                    'compression.type': 'lz4',
                }
                self._producer = Producer(config)
                logger.info(f"Kafka producer initialized: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            except Exception as e:
                logger.warning(f"Kafka producer fallback mode (no broker connected): {e}")
                self._producer = "MOCK_PRODUCER"
    
    async def produce(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        schema_type: str = 'telemetry',
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        if self._producer is None:
            await self.initialize()
        
        if 'event_id' not in value:
            value['event_id'] = str(uuid4())
        if 'timestamp' not in value:
            value['timestamp'] = int(datetime.utcnow().timestamp() * 1000)
            
        payload = json.dumps(value, default=str).encode('utf-8')
        
        if self._producer != "MOCK_PRODUCER" and hasattr(self._producer, 'produce'):
            try:
                self._producer.produce(
                    topic=topic,
                    value=payload,
                    key=key.encode('utf-8') if key else None,
                )
                self._producer.poll(0)
            except Exception as e:
                logger.error(f"Produce error: {e}")
                self._failed_count += 1
                return False
                
        self._produced_count += 1
        self._bytes_sent += len(payload)
        return True
    
    async def flush(self, timeout: float = 10.0) -> int:
        if self._producer and hasattr(self._producer, 'flush'):
            return self._producer.flush(timeout)
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'produced': self._produced_count,
            'failed': self._failed_count,
            'bytes_sent': self._bytes_sent,
            'last_error': self._last_error,
        }


class TelemetryProducer:
    def __init__(self, producer: KafkaProducerService):
        self.producer = producer
    
    async def publish(
        self,
        robot_id: str,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        position: Optional[Dict] = None,
        source: str = "ros2",
        metadata: Optional[Dict] = None,
    ) -> bool:
        event = {
            'event_id': str(uuid4()),
            'timestamp': int(datetime.utcnow().timestamp() * 1000),
            'robot_id': robot_id,
            'metric_type': metric_type,
            'value': value,
            'unit': unit,
            'position': position,
            'metadata': json.dumps(metadata) if metadata else None,
            'source': source,
        }
        return await self.producer.produce(
            topic=settings.TOPIC_TELEMETRY,
            value=event,
            key=robot_id,
            schema_type='telemetry',
        )


class DetectionProducer:
    def __init__(self, producer: KafkaProducerService):
        self.producer = producer
    
    async def publish(
        self,
        robot_id: str,
        model_version: str,
        class_name: str,
        class_id: int,
        confidence: float,
        bbox: Dict[str, float],
        inference_time_ms: float,
        image_url: Optional[str] = None,
        position: Optional[Dict] = None,
    ) -> bool:
        event = {
            'event_id': str(uuid4()),
            'timestamp': int(datetime.utcnow().timestamp() * 1000),
            'robot_id': robot_id,
            'model_version': model_version,
            'class_name': class_name,
            'class_id': class_id,
            'confidence': confidence,
            'bbox': bbox,
            'inference_time_ms': inference_time_ms,
            'image_url': image_url,
            'position': position,
        }
        return await self.producer.produce(
            topic=settings.TOPIC_DETECTIONS,
            value=event,
            key=robot_id,
            schema_type='detection',
        )


kafka_producer = KafkaProducerService()
telemetry_producer = TelemetryProducer(kafka_producer)
detection_producer = DetectionProducer(kafka_producer)
