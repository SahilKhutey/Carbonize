"""
Stream processors that consume Kafka and route to fan-out
"""
import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime

from app.consumers.kafka_consumer import KafkaConsumerService, ConsumedMessage
from app.websocket.fanout_manager import fanout_manager
from app.storage.timeseries_db import timeseries_db
from app.config import settings

logger = logging.getLogger(__name__)


class TelemetryStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-telemetry-processor',
            topics=[settings.TOPIC_TELEMETRY],
        )
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(
            settings.TOPIC_TELEMETRY,
            self.handle_telemetry,
        )
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Telemetry stream processor started")
    
    async def handle_telemetry(self, msg: ConsumedMessage):
        event = msg.value
        await timeseries_db.write_telemetry(event)
        await fanout_manager.broadcast_event('telemetry', event)
        
        if event.get('metric_type') == 'co2_ppm' and event.get('value', 0) > 1000:
            alert = {
                'event_id': f"alert_{event.get('event_id')}",
                'timestamp': int(datetime.utcnow().timestamp() * 1000),
                'alert_type': 'co2_high',
                'severity': 'warning',
                'message': f"High CO2 concentration: {event.get('value'):.0f} ppm",
                'source_id': event.get('robot_id'),
                'context': json.dumps(event),
            }
            await fanout_manager.broadcast_event('alert', alert)


class DetectionStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-detection-processor',
            topics=[settings.TOPIC_DETECTIONS],
        )
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(
            settings.TOPIC_DETECTIONS,
            self.handle_detection,
        )
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Detection stream processor started")
    
    async def handle_detection(self, msg: ConsumedMessage):
        event = msg.value
        await timeseries_db.write_detection(event)
        await fanout_manager.broadcast_event('detection', event)


class AggregateStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-aggregate-processor',
            topics=[settings.TOPIC_AGGREGATES],
        )
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(
            settings.TOPIC_AGGREGATES,
            self.handle_aggregate,
        )
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Aggregate stream processor started")
    
    async def handle_aggregate(self, msg: ConsumedMessage):
        event = msg.value
        await timeseries_db.write_aggregate(event)
        await fanout_manager.broadcast_event('aggregate', event)


class AnomalyStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-anomaly-processor',
            topics=[settings.TOPIC_ANOMALIES],
        )
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(
            settings.TOPIC_ANOMALIES,
            self.handle_anomaly,
        )
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Anomaly stream processor started")
    
    async def handle_anomaly(self, msg: ConsumedMessage):
        event = msg.value
        await fanout_manager.broadcast_event('anomaly', event)


telemetry_processor = TelemetryStreamProcessor()
detection_processor = DetectionStreamProcessor()
aggregate_processor = AggregateStreamProcessor()
anomaly_processor = AnomalyStreamProcessor()
