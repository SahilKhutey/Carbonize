"""
Streaming API with WebSocket endpoints
"""
import asyncio
import json
import logging
from typing import Optional, List, Dict
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from app.websocket.fanout_manager import fanout_manager, Subscription
from app.producers.kafka_producer import kafka_producer, telemetry_producer
from app.storage.timeseries_db import timeseries_db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/stream", tags=["streaming"])


class PublishRequest(BaseModel):
    robot_id: str
    metric_type: str
    value: float
    unit: Optional[str] = None
    position: Optional[Dict] = None
    source: str = 'api'


@router.websocket("/ws")
async def stream_websocket(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
):
    await websocket.accept()
    
    if client_id is None:
        client_id = str(uuid4())
    
    state = await fanout_manager.add_client(websocket, client_id, user_id)
    
    await websocket.send_json({
        'type': 'welcome',
        'client_id': client_id,
        'server_time': int(datetime.utcnow().timestamp() * 1000),
        'protocol_version': '1.0',
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({'type': 'error', 'message': 'Invalid JSON'})
                continue
            
            msg_type = msg.get('type')
            
            if msg_type == 'subscribe':
                sub = msg.get('subscription', {})
                subscription = Subscription(
                    robot_id=sub.get('robot_id'),
                    metric_types=set(sub.get('metric_types', [])),
                    classes=set(sub.get('classes', [])),
                    min_severity=sub.get('min_severity', 'info'),
                )
                await fanout_manager.update_subscription(client_id, subscription)
                await websocket.send_json({'type': 'subscribe_ack', 'subscription': sub})
            
            elif msg_type == 'ping':
                await websocket.send_json({'type': 'pong', 'timestamp': int(datetime.utcnow().timestamp() * 1000)})
            
            elif msg_type == 'get_stats':
                stats = fanout_manager.get_stats()
                await websocket.send_json({'type': 'stats', 'data': stats})
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        await fanout_manager.remove_client(client_id)


@router.post("/publish/telemetry")
async def publish_telemetry(payload: PublishRequest):
    success = await telemetry_producer.publish(
        robot_id=payload.robot_id,
        metric_type=payload.metric_type,
        value=payload.value,
        unit=payload.unit,
        position=payload.position,
        source=payload.source,
    )
    return {'status': 'published' if success else 'failed'}


@router.get("/query/{metric_type}")
async def query_metric(
    metric_type: str,
    robot_id: Optional[str] = None,
    range: str = '-1h',
    window: str = '1m',
):
    data = await timeseries_db.query_metric(
        metric_type=metric_type,
        robot_id=robot_id,
        range_start=range,
        aggregation_window=window,
    )
    return {'metric_type': metric_type, 'data': data, 'count': len(data)}


@router.get("/stats")
async def get_stats():
    return {
        'fanout': fanout_manager.get_stats(),
        'producer': kafka_producer.get_stats(),
    }
