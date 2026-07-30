"""
Pilot DAQ Stream Manager
"""
from typing import Dict


class PilotDAQManager:
    def stream_telemetry(self) -> Dict:
        return {'pressure_bar': 1.8, 'temperature_C': 40.2, 'flow_rate_L_min': 12.4}
