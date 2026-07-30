"""
Anomaly detection stream processor
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import json

from app.anomaly.autoencoder import StreamingAutoencoderDetector
from app.anomaly.streaming_isoforest import StreamingIsolationForest
from app.anomaly.multimodal import MultiModalAnomalyDetector
from app.consumers.kafka_consumer import KafkaConsumerService
from app.producers.kafka_producer import kafka_producer
from app.websocket.fanout_manager import fanout_manager
from app.config import settings


logger = logging.getLogger(__name__)


class AnomalyStreamProcessor:
    """Real-time anomaly detection on streaming data."""
    
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-anomaly-detector',
            topics=[settings.TOPIC_TELEMETRY],
        )
        
        self._autoencoders: Dict[str, StreamingAutoencoderDetector] = {}
        self._isoforests: Dict[str, StreamingIsolationForest] = {}
        self._multimodal: MultiModalAnomalyDetector = MultiModalAnomalyDetector()
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(
            settings.TOPIC_TELEMETRY,
            self.handle_telemetry,
        )
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Anomaly stream processor started")
    
    async def handle_telemetry(self, msg):
        """Process telemetry event for anomaly detection."""
        event = msg.value
        metric_type = event.get('metric_type')
        robot_id = event.get('robot_id')
        value = event.get('value')
        
        if metric_type is None or value is None:
            return
        
        key = f"{metric_type}_{robot_id}"
        
        if key not in self._autoencoders:
            self._autoencoders[key] = StreamingAutoencoderDetector(
                feature_dim=1,
                sequence_length=60,
                hidden_dim=64,
                model_type='lstm',
            )
        
        ae_result = self._autoencoders[key].add_value(float(value))
        
        if key not in self._isoforests:
            self._isoforests[key] = StreamingIsolationForest(
                n_trees=100,
                window_size=1000,
            )
        
        if_result = self._isoforests[key].add_sample(float(value))
        mm_result = self._multimodal.add_value(metric_type, float(value), robot_id)
        
        anomaly = self._combine_detections(metric_type, robot_id, value, ae_result, if_result, mm_result)
        
        if anomaly and anomaly['is_anomaly']:
            await self._emit_anomaly(anomaly)
    
    def _combine_detections(self, metric_type, robot_id, value, ae_result, if_result, mm_result) -> Optional[Dict]:
        """Combine multiple detector results."""
        if not all([ae_result, if_result, mm_result]):
            return None
        
        scores = {
            'autoencoder': ae_result['score'],
            'isolation_forest': if_result['score'],
            'multimodal': mm_result['confidence'],
        }
        
        weights = {'autoencoder': 0.4, 'isolation_forest': 0.3, 'multimodal': 0.3}
        weighted_score = sum(scores[k] * weights[k] for k in scores)
        consensus = sum(1 for s in scores.values() if s > 0.7)
        
        threshold = 0.5
        is_anomaly = weighted_score >= threshold or consensus >= 2
        
        if not is_anomaly:
            return None
        
        return {
            'timestamp': int(datetime.utcnow().timestamp() * 1000),
            'metric_type': metric_type,
            'source_id': robot_id,
            'value': float(value),
            'scores': scores,
            'weighted_score': weighted_score,
            'is_anomaly': True,
            'severity': self._get_severity(weighted_score),
            'correlated_anomalies': mm_result.get('correlated_anomalies', []),
        }
    
    def _get_severity(self, score: float) -> str:
        if score >= 0.85:
            return 'critical'
        elif score >= 0.7:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    async def _emit_anomaly(self, anomaly: Dict):
        """Emit anomaly to alert system."""
        alert = {
            'event_id': f"anomaly_{anomaly['timestamp']}",
            'timestamp': anomaly['timestamp'],
            'alert_type': 'ml_anomaly',
            'severity': anomaly['severity'],
            'message': f"ML anomaly detected in {anomaly['metric_type']} (score={anomaly['weighted_score']:.2f})",
            'source_id': anomaly['source_id'],
            'context': json.dumps(anomaly),
        }
        
        await fanout_manager.broadcast_event('anomaly', alert)
        await kafka_producer.produce(
            topic=settings.TOPIC_ANOMALIES,
            value=anomaly,
            key=f"{anomaly['metric_type']}_{anomaly['source_id']}",
            schema_type='aggregate',
        )


anomaly_processor = AnomalyStreamProcessor()
