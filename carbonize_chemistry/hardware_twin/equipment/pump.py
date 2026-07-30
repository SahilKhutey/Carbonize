"""
Pump & Compressor models
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class Pump:
    rated_flow: float = 300.0
    rated_head: float = 15.0
    efficiency: float = 0.75
    speed: float = 1.0
    current_flow: float = 0.0
    current_head: float = 0.0
    
    def update(self, flow: float, fluid_density: float = 1000.0):
        self.current_flow = min(flow, self.rated_flow * self.speed)
        self.current_head = self.rated_head * ((self.current_flow / max(self.rated_flow, 1e-5)) ** 2)
    
    def power_consumption(self) -> float:
        if self.current_flow <= 0:
            return 0.0
        hydraulic_power = 1000.0 * 9.81 * (self.current_flow / 3600.0) * self.current_head
        return float(hydraulic_power / self.efficiency)


class Compressor:
    def __init__(self, rated_flow: float = 500.0, rated_PR: float = 1.05, efficiency: float = 0.80):
        self.rated_flow = rated_flow
        self.rated_PR = rated_PR
        self.efficiency = efficiency
        self.current_flow = 0.0
        self.current_PR = 1.0
    
    def update(self, flow: float, P_in: float):
        self.current_flow = min(flow, self.rated_flow)
        self.current_PR = self.rated_PR * (1.0 - 0.2 * ((self.current_flow / self.rated_flow)**2))
    
    def power_consumption(self) -> float:
        if self.current_flow <= 0:
            return 0.0
        return float(1.2 * (self.current_flow / 3600.0) * 350.0 * np.log(self.current_PR) / self.efficiency)
