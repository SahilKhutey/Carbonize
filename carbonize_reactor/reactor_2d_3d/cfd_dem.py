"""
CFD-DEM Packed Bed Particle Simulation
"""
import numpy as np
from dataclasses import dataclass, field


@dataclass
class PackedBedGeometry:
    column_diameter: float = 0.05
    column_height: float = 0.5
    particle_diameter: float = 0.003
    n_particles: int = 500


class CFSDEM_PackedBed:
    def __init__(self, geom: PackedBedGeometry):
        self.geom = geom
        self.positions = np.zeros((geom.n_particles, 3))
        self.generate()

    def generate(self):
        for i in range(self.geom.n_particles):
            r = np.random.uniform(0, self.geom.column_diameter / 2.0 * 0.9)
            theta = np.random.uniform(0, 2.0 * np.pi)
            z = np.random.uniform(0, self.geom.column_height)
            self.positions[i] = [r * np.cos(theta), r * np.sin(theta), z]
