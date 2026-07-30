"""
Stream processor for real-time drift detection
"""
import asyncio
import json
import logging
from typing import Dict
from datetime import datetime

from app.drift.drift_detector import StreamingDriftDetector, ConceptDriftDetector
from app.consumers.kafka_consumer import KafkaConsumerService
from app.producers.kafka_producer import kafka_producer
from app.websocket.fanout_manager import fanout_manager
from app.config import settings

logger = logging.getLogger(__name__)


class DriftStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumerService(
            group_id='carbonize-drift-detector',
            topics=[settings.TOPIC_TELEMETRY, settings.TOPIC_DETECTIONS],
        )
        self._detectors: Dict[str, StreamingDriftDetector] = {}
        self._concept_detectors: Dict[str, ConceptDriftDetector] = {}
    
    async def start(self):
        await self.consumer.initialize()
        self.consumer.register_handler(settings.TOPIC_TELEMETRY, self.handle_telemetry)
        self.consumer.register_handler(settings.TOPIC_DETECTIONS, self.handle_detection)
        asyncio.create_task(self.consumer.consume_loop())
        logger.info("Drift stream processor started")
    
    async def handle_telemetry(self, msg):
        event = msg.value
        metric_type = event.get('metric_type')
        robot_id = event.get('robot_id')
        val = event.get('value')
        
        if not metric_type or val is None:
            return
        
        key = f"{metric_type}_{robot_id or 'sys'}"
        if key not in self._detectors:
            self._detectors[key] = StreamingDriftDetector(metric_type=key)
        
        detector = self._detectors[key]
        detector.add_value(float(val))
        
        summary = detector.check_drift()
        if summary and summary.overall_drifted:
            alert = {
                'event_id': f"drift_{int(datetime.utcnow().timestamp()*1000)}",
                'timestamp': summary.timestamp,
                'alert_type': 'data_drift',
                'severity': 'warning',
                'message': f"Data drift detected in {key} (score={summary.overall_score:.2f})",
                'source_id': key,
                'context': json.dumps({'overall_score': summary.overall_score}),
            }
            await fanout_manager.broadcast_event('drift', alert)
            await fanout_manager.broadcast_event('drift_summary', {
                'detector_key': key,
                'timestamp': summary.timestamp,
                'overall_drifted': summary.overall_drifted,
                'overall_score': summary.overall_score,
                'recommendation': summary.recommended_action,
            })
    
    async def handle_detection(self, msg):
        event = msg.value
        model_id = event.get('model_version', '1.5.0')
        
        if model_id not in self._concept_detectors:
            self._concept_detectors[model_id] = ConceptDriftDetector(model_id=model_id)
        
        detector = self._concept_detectors[model_id]
        detector.record_prediction(event, event.get('ground_truth'))
        res = detector.check_drift()
        if res.get('drift_detected'):
            alert = {
                'event_id': f"concept_drift_{int(datetime.utcnow().timestamp()*1000)}",
                'timestamp': int(datetime.utcnow().timestamp()*1000),
                'alert_type': 'concept_drift',
                'severity': 'critical',
                'message': f"Concept drift detected for model {model_id}",
                'source_id': model_id,
            }
            await fanout_manager.broadcast_event('drift', alert)
    
    def get_all_states(self) -> Dict:
        return {
            'data_drift': {
                k: {
                    'history': [
                        {
                            'timestamp': s.timestamp,
                            'overall_drifted': s.overall_drifted,
                            'overall_score': s.overall_score,
                            'recommendation': s.recommended_action,
                        }
                        for s in v.get_history(20)
                    ]
                }
                for k, v in self._detectors.items()
            },
            'concept_drift': {
                k: v.check_drift()
                for k, v in self._concept_detectors.items()
            },
        }


drift_processor = DriftStreamProcessor()
