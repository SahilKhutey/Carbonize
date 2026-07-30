"""
Complete Carbon Capture Plant Digital Twin
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import time

from .equipment.pump import Pump, Compressor
from .equipment.heat_exchanger import HeatExchanger
from .equipment.sensor import SensorModel
from .control.pid import PIDController
from ..columns.tray_column import TrayColumnSolver, ColumnSpec, StreamConditions


@dataclass
class PlantState:
    timestamp: float
    flue_gas: Dict = field(default_factory=dict)
    lean_solvent: Dict = field(default_factory=dict)
    rich_solvent: Dict = field(default_factory=dict)
    captured_CO2: Dict = field(default_factory=dict)
    vent_gas: Dict = field(default_factory=dict)
    CO2_capture_rate: float = 0.0
    CO2_capture_efficiency: float = 0.0
    reboiler_duty: float = 0.0
    energy_consumption: float = 0.0
    alarms: List[Dict] = field(default_factory=list)


class CarbonCapturePlant:
    """Complete Digital Twin plant model."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.amine = self.config.get('amine', 'MEA')
        
        self.absorber = ColumnSpec(n_trays=20, diameter=4.0, pressure=101325.0)
        self.stripper = ColumnSpec(n_trays=15, diameter=3.5, pressure=180000.0)
        self.absorber_solver = TrayColumnSolver(self.absorber, amine=self.amine)
        self.stripper_solver = TrayColumnSolver(self.stripper, amine=self.amine)
        
        self.reboiler = HeatExchanger(duty_max=50e6, area=2000.0)
        self.lean_pump = Pump(rated_flow=300.0, rated_head=15.0)
        self.blower = Compressor(rated_flow=500.0, rated_PR=1.05)
        
        self.sensors = {
            'flue_gas_flow': SensorModel('flow', 'm3/h', (100, 1000), noise_sigma=0.01),
            'flue_gas_CO2': SensorModel('composition', 'mole_fraction', (0, 0.20), noise_sigma=0.001),
            'lean_loading': SensorModel('composition', 'mol_CO2/mol_amine', (0, 0.5), noise_sigma=0.01),
        }
        
        self.controllers = {
            'lean_flow': PIDController(Kp=0.5, Ki=0.1, Kd=0.05, setpoint=300.0, output_min=100.0, output_max=500.0),
        }
        
        self.state = PlantState(
            timestamp=time.time(),
            flue_gas={'flow': 500.0, 'CO2': 0.13, 'T': 318.0},
            lean_solvent={'flow': 300.0, 'loading': 0.10, 'T': 313.0},
            rich_solvent={'flow': 300.0, 'loading': 0.45, 'T': 333.0},
        )
    
    async def step(self, dt: float = 5.0, disturbances: Optional[Dict] = None) -> PlantState:
        m_flow = self.sensors['flue_gas_flow'].read(self.state.flue_gas['flow'])
        m_co2 = self.sensors['flue_gas_CO2'].read(self.state.flue_gas['CO2'])
        
        lean_flow = self.controllers['lean_flow'].update(setpoint=300.0, measurement=m_flow, dt=dt)
        
        gas_in = StreamConditions(T=318.0, P=101325.0, flow=m_flow, composition={'CO2': m_co2})
        liq_in = StreamConditions(T=313.0, P=101325.0, flow=lean_flow, composition={'CO2': 0.10})
        
        abs_res = self.absorber_solver.solve(gas_in, liq_in)
        
        eff = max(0.0, (1.0 - abs_res['gas_out']['CO2_mol_frac'] / max(m_co2, 1e-5)) * 100.0)
        capture_rate = m_flow * m_co2 * 0.90 * (44.01 / 22.414)
        
        self.state.timestamp = time.time()
        self.state.CO2_capture_efficiency = float(eff)
        self.state.CO2_capture_rate = float(capture_rate)
        self.state.reboiler_duty = float(capture_rate * 3.5 / 3600.0)
        self.state.energy_consumption = float(self.state.reboiler_duty * 3600.0)
        self.state.lean_solvent['flow'] = float(lean_flow)
        
        return self.state
