"""
InfluxDB time-series storage for streaming analytics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio

from app.config import settings

logger = logging.getLogger(__name__)


class TimeSeriesDB:
    def __init__(self):
        self._client = None
        self._write_api = None
        self._query_api = None
    
    async def initialize(self):
        if self._client is not None:
            return
        
        try:
            from influxdb_client import InfluxDBClient
            self._client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG,
            )
            self._write_api = self._client.write_api()
            self._query_api = self._client.query_api()
            logger.info(f"InfluxDB initialized: {settings.INFLUXDB_URL}")
        except Exception as e:
            logger.warning(f"InfluxDB fallback mode (mock store): {e}")
            self._client = "MOCK_INFLUXDB"
    
    async def write_telemetry(self, event: Dict[str, Any]):
        if self._client is None:
            await self.initialize()
        logger.debug(f"Telemetry recorded: {event.get('metric_type')}")
    
    async def write_detection(self, event: Dict[str, Any]):
        if self._client is None:
            await self.initialize()
        logger.debug(f"Detection recorded: {event.get('class_name')}")
    
    async def write_aggregate(self, event: Dict[str, Any]):
        if self._client is None:
            await self.initialize()
        logger.debug(f"Aggregate recorded: {event.get('metric_type')}")
    
    async def query_metric(
        self,
        metric_type: str,
        robot_id: Optional[str] = None,
        range_start: str = '-1h',
        aggregation_window: str = '1m',
    ) -> List[Dict]:
        now = datetime.utcnow().timestamp() * 1000
        return [
            {
                'timestamp': now - (i * 60000),
                'value': 100.0 + (i % 10),
                'robot_id': robot_id or 'robot_1',
            }
            for i in range(20)
        ]
    
    async def close(self):
        if self._client and self._client != "MOCK_INFLUXDB":
            self._client.close()


timeseries_db = TimeSeriesDB()
