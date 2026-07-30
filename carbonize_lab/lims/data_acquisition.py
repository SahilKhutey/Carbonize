"""
Real-time Data Acquisition (DAQ) System
"""
import numpy as np
import time
from typing import Dict, List, Callable
from dataclasses import dataclass, field


@dataclass
class DAQChannel:
    name: str
    sensor_type: str
    units: str
    sample_rate_hz: float = 1.0
    offset: float = 0.0
    scale: float = 1.0
    history: List[float] = field(default_factory=list)

    def read(self, raw_value: float) -> float:
        calibrated = float(raw_value * self.scale + self.offset)
        self.history.append(calibrated)
        return calibrated


class DAQSystem:
    def __init__(self, rig_id: str):
        self.rig_id = rig_id
        self.channels: Dict[str, DAQChannel] = {}

    def add_channel(self, channel: DAQChannel):
        self.channels[channel.name] = channel

    def read_all(self) -> Dict:
        return {name: ch.read(np.random.normal(100.0, 2.0)) for name, ch in self.channels.items()}
