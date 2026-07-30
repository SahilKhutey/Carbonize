"""
Standard Verlet Integrator
"""
import numpy as np

class Verlet:
    def __init__(self, dt: float = 0.001):
        self.dt = dt
