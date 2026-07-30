"""
Instrument Integration (FTIR, GC-MS, HPLC, pH Meter, Balance)
"""
import time
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class MeasurementConfig:
    method: str = ''
    parameters: Dict = field(default_factory=dict)
    expected_duration_s: float = 60.0


@dataclass
class MeasurementResult:
    timestamp: float
    instrument: str
    method: str
    raw_data: Dict
    processed_data: Dict = field(default_factory=dict)


class InstrumentBase(ABC):
    def __init__(self, name: str, address: str = ''):
        self.name = name
        self.address = address
        self.connected = False

    @abstractmethod
    def connect(self) -> bool: pass
    @abstractmethod
    def disconnect(self) -> bool: pass
    @abstractmethod
    def measure(self, config: MeasurementConfig) -> MeasurementResult: pass


class FTIRInstrument(InstrumentBase):
    def __init__(self, address: str):
        super().__init__('FTIR', address)

    def connect(self) -> bool: self.connected = True; return True
    def disconnect(self) -> bool: self.connected = False; return True

    def measure(self, config: MeasurementConfig) -> MeasurementResult:
        w = np.linspace(500, 4000, 100).tolist()
        i = (0.1 + 0.7 * np.exp(-((np.array(w) - 2350) / 30) ** 2)).tolist()
        return MeasurementResult(
            timestamp=time.time(),
            instrument='FTIR',
            method=config.method,
            raw_data={'wavelengths': w, 'intensity': i},
            processed_data={'CO2_peak_area': 14.5, 'peak_position': 2350.0},
        )


class GCMSInstrument(InstrumentBase):
    def __init__(self, address: str):
        super().__init__('GC-MS', address)

    def connect(self) -> bool: self.connected = True; return True
    def disconnect(self) -> bool: self.connected = False; return True

    def measure(self, config: MeasurementConfig) -> MeasurementResult:
        return MeasurementResult(
            timestamp=time.time(),
            instrument='GC-MS',
            method=config.method,
            raw_data={'retention_times': [5.0, 10.0, 15.0], 'chromatogram': [100.0, 80.0, 60.0]},
            processed_data={'n_peaks': 3, 'peak_areas': [100.0, 80.0, 60.0]},
        )


class HPLCInstrument(InstrumentBase):
    def __init__(self, address: str):
        super().__init__('HPLC', address)

    def connect(self) -> bool: self.connected = True; return True
    def disconnect(self) -> bool: self.connected = False; return True

    def measure(self, config: MeasurementConfig) -> MeasurementResult:
        return MeasurementResult(
            timestamp=time.time(),
            instrument='HPLC',
            method=config.method,
            raw_data={'time': [3.0, 7.5, 12.0], 'chromatogram': [100.0, 50.0, 80.0]},
            processed_data={'n_peaks': 3, 'peak_areas': [100.0, 50.0, 80.0]},
        )


class pHMeter(InstrumentBase):
    def __init__(self, address: str):
        super().__init__('pH_Meter', address)

    def connect(self) -> bool: self.connected = True; return True
    def disconnect(self) -> bool: self.connected = False; return True

    def measure(self, config: MeasurementConfig) -> MeasurementResult:
        return MeasurementResult(timestamp=time.time(), instrument='pH_Meter', method='direct', raw_data={'pH': 10.5, 'mV': -250.0, 'T': 298.15})


class Balance(InstrumentBase):
    def __init__(self, address: str):
        super().__init__('Balance', address)

    def connect(self) -> bool: self.connected = True; return True
    def disconnect(self) -> bool: self.connected = False; return True

    def measure(self, config: MeasurementConfig) -> MeasurementResult:
        return MeasurementResult(timestamp=time.time(), instrument='Balance', method='direct', raw_data={'mass': 100.5234, 'unit': 'g'})
