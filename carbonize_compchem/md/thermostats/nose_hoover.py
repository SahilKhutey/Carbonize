"""
Nose-Hoover, Langevin, and Berendsen Thermostats
"""
import numpy as np


class NoseHooverThermostat:
    def __init__(self, target_T: float, tau_T: float = 1.0):
        self.target_T = target_T
        self.tau_T = tau_T
        self.xi = 0.0

    def apply(self, state, masses: np.ndarray, dt: float):
        T_curr = state.temperature
        if T_curr > 0:
            scale = np.sqrt(1.0 + (dt / self.tau_T) * (self.target_T / T_curr - 1.0))
            state.velocities *= scale
        return state


class LangevinThermostat:
    def __init__(self, target_T: float, gamma: float = 1.0):
        self.target_T = target_T
        self.gamma = gamma

    def apply(self, state, masses: np.ndarray, dt: float):
        k_B = 8.314e-3
        sigma = np.sqrt(2.0 * k_B * self.target_T * self.gamma * dt)
        for i in range(len(masses)):
            F_rand = np.random.normal(0, sigma * np.sqrt(masses[i]))
            state.velocities[i] += (F_rand - self.gamma * masses[i] * state.velocities[i]) / masses[i] * dt
        return state


class BerendsenThermostat:
    def __init__(self, target_T: float, tau_T: float = 0.1):
        self.target_T = target_T
        self.tau_T = tau_T

    def apply(self, state, masses: np.ndarray, dt: float):
        T_curr = state.temperature
        if T_curr > 0:
            scale = np.sqrt(1.0 + (dt / self.tau_T) * (self.target_T / T_curr - 1.0))
            state.velocities *= scale
        return state
