"""
Base classes and abstractions for all reactor models
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


@dataclass
class ReactorGeometry:
    length: float = 2.0
    diameter: float = 0.05
    cross_section_area: float = 0.0
    volume: float = 0.0
    particle_diameter: float = 0.003
    bed_porosity: float = 0.40
    particle_porosity: float = 0.50
    particle_density: float = 2200.0
    tortuosity: float = 3.0
    channel_density: float = 0.0
    wall_thickness: float = 0.0001
    washcoat_thickness: float = 0.00005
    washcoat_porosity: float = 0.40

    def __post_init__(self):
        if self.cross_section_area == 0.0:
            self.cross_section_area = np.pi * (self.diameter ** 2) / 4.0
        if self.volume == 0.0:
            self.volume = self.length * self.cross_section_area


@dataclass
class OperatingConditions:
    T_in: float = 573.15
    P_in: float = 101325.0
    flow_gas: float = 1.0
    flow_liquid: float = 0.0
    y_in: Dict[str, float] = field(default_factory=dict)
    x_in: Dict[str, float] = field(default_factory=dict)
    T_wall: float = 573.15
    heat_exchange_coeff: float = 0.0
    isothermal: bool = True


@dataclass
class ReactionNetwork:
    reactions: List[Dict] = field(default_factory=list)
    species: List[str] = field(default_factory=list)


class ReactorState:
    z: np.ndarray = None
    T: np.ndarray = None
    P: np.ndarray = None
    y: Dict[str, np.ndarray] = None
    c: Dict[str, np.ndarray] = None
    v_g: np.ndarray = None
    v_l: np.ndarray = None
    conversion: Dict[str, float] = field(default_factory=dict)
    selectivity: Dict[str, float] = field(default_factory=dict)
    yield_: Dict[str, float] = field(default_factory=dict)
    pressure_drop: float = 0.0
    heat_duty: float = 0.0
    space_time: float = 0.0
    ghsv: float = 0.0


class ReactorBase(ABC):
    def __init__(self, geometry: ReactorGeometry, operating: OperatingConditions, reactions: ReactionNetwork):
        self.geom = geometry
        self.op = operating
        self.reactions = reactions
        self.state = ReactorState()
        self.max_iterations = 500
        self.tolerance = 1e-6

    @abstractmethod
    def solve(self, n_points: int = 100) -> ReactorState:
        pass

    def space_velocity(self) -> float:
        Q_gas = self.op.flow_gas * 22.414e-3 * (self.op.T_in / 273.15) * (101325.0 / max(self.op.P_in, 1e-5)) * 3600.0
        V_bed = self.geom.volume * self.geom.bed_porosity
        return Q_gas / max(V_bed, 1e-6)

    def weight_time(self) -> float:
        W = self.geom.volume * (1.0 - self.geom.bed_porosity) * self.geom.particle_density
        return W / max(self.op.flow_gas, 1e-6)

    def _gas_velocity(self) -> float:
        Q = self.op.flow_gas * 8.314 * self.op.T_in / max(self.op.P_in, 1e-5)
        return Q / max(self.geom.cross_section_area, 1e-6)
