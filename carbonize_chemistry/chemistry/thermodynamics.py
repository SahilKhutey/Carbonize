"""
Engineering thermodynamics for process calculations
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from .constants import R_GAS, get_critical_properties, get_molar_mass


@dataclass
class CPParams:
    """Shomate-style heat capacity parameters."""
    a: float
    b: float
    c: float
    d: float
    e: float
    T_min: float
    T_max: float


HEAT_CAPACITY_PARAMS = {
    'CO2': CPParams(24.99735, 55.18696, -33.69137, 7.948387, -0.136638, 298.0, 1200.0),
    'H2O': CPParams(30.09200, 6.832514, 6.793435, -2.534480, 0.082139, 298.0, 1700.0),
    'N2':  CPParams(26.09200, 8.218801, -1.976141, 0.159274, 0.044434, 298.0, 6000.0),
    'O2':  CPParams(30.03200, 8.772972, -3.988133, 0.788313, -0.741599, 298.0, 6000.0),
    'H2S': CPParams(29.73720, 15.61340, -3.131340, 0.273800, 0.006600, 298.0, 1000.0),
    'SO2': CPParams(25.74800, 57.91100, -38.40500, 8.948000, -0.730000, 298.0, 1200.0),
    'MEA': CPParams(26.50, 250.0, -150.0, 35.0, -3.0, 298.0, 800.0),
    'MDEA': CPParams(35.0, 320.0, -180.0, 40.0, -3.5, 298.0, 800.0),
}


def heat_capacity_gas(compound: str, T: float) -> float:
    """Heat capacity of ideal gas at temperature T (K) in J/(mol·K)."""
    if compound not in HEAT_CAPACITY_PARAMS:
        return 35.0
    params = HEAT_CAPACITY_PARAMS[compound]
    t = T / 1000.0
    return (params.a + params.b * t + params.c * t**2 + params.d * t**3 + params.e / (t**2 + 1e-10))


def heat_capacity_liquid(compound: str, T: float) -> float:
    """Heat capacity of liquid at temperature T (K) in J/(kg·K)."""
    if compound == 'H2O':
        return 4.217e3 - 2.0 * (T - 273.15)
    if compound == 'MEA':
        return 3.9e3 + 2.5e2 * (T - 313.0) / 10.0
    if compound == 'MDEA':
        return 3.6e3 + 1.8e2 * (T - 313.0) / 10.0
    return 4000.0


def enthalpy_ideal_gas(compound: str, T: float, T_ref: float = 298.15) -> float:
    """Enthalpy of ideal gas from T_ref to T in J/mol."""
    cp = heat_capacity_gas(compound, (T + T_ref) / 2.0)
    return cp * (T - T_ref)


def vapor_pressure(compound: str, T: float) -> float:
    """Vapor pressure using Antoine equation in Pa."""
    ANTOINE = {
        'H2O':  (8.07131, 1730.63, 233.426),
        'MEA':  (4.53493, 1351.55, -86.43),
        'MDEA': (4.89967, 1704.34, -71.38),
        'Piperazine': (4.62871, 1384.27, -73.81),
        'CO2':  (6.81228, 1301.679, -3.494),
        'H2S':  (4.43606, 829.439, -25.412),
        'SO2':  (4.37702, 966.827, -42.071),
    }
    if compound not in ANTOINE:
        return 101325.0
    A, B, C = ANTOINE[compound]
    T_celsius = T - 273.15
    log_p_mmhg = A - B / (T_celsius + C + 1e-10)
    P_mmhg = 10 ** log_p_mmhg
    return float(P_mmhg * 133.322)


def density_ideal_gas(compound: str, T: float, P: float) -> float:
    """Density of ideal gas in kg/m³."""
    M = get_molar_mass(compound) / 1000.0
    return float(P * M / (R_GAS * T))


def density_liquid(compound: str, T: float) -> float:
    """Liquid density in kg/m³."""
    if compound == 'H2O':
        return 1000.0 - 0.01 * (T - 293.15)**2
    if compound in ('MEA', 'MDEA', 'Piperazine'):
        return 1020.0 - 0.5 * (T - 293.15)
    return 1000.0


def viscosity_gas(compound: str, T: float) -> float:
    """Gas viscosity using Sutherland equation in Pa·s."""
    SUTHERLAND = {
        'CO2': (1.48e-5, 273.0, 240.0),
        'N2':  (1.66e-5, 273.0, 104.7),
        'O2':  (1.92e-5, 273.0, 138.4),
        'H2O': (1.27e-5, 273.0, 650.0),
        'Air': (1.71e-5, 273.0, 124.0),
    }
    item = SUTHERLAND.get(compound, SUTHERLAND['Air'])
    mu_ref, T_ref, S = item
    return float(mu_ref * (T / T_ref)**1.5 * (T_ref + S) / (T + S))


def viscosity_liquid(compound: str, T: float) -> float:
    """Liquid viscosity using Andrade equation in Pa·s."""
    ANDRADE = {
        'H2O':   (1.856e-5, 1659.0),
        'MEA':   (3.0e-6,   2200.0),
        'MDEA':  (1.5e-6,   2500.0),
    }
    if compound not in ANDRADE:
        return 1e-3
    A, B = ANDRADE[compound]
    return float(A * np.exp(B / T))


def diffusivity_gas(compound_1: str, compound_2: str, T: float, P: float) -> float:
    """Binary gas diffusivity in m²/s."""
    M1 = get_molar_mass(compound_1) / 1000.0
    M2 = get_molar_mass(compound_2) / 1000.0
    return float(1.0e-5 * (T / 298.15)**1.75 / (P / 101325.0))


def diffusivity_liquid(compound: str, solvent: str = 'H2O', T: float = 298.15) -> float:
    """Liquid diffusivity in m²/s."""
    mu = viscosity_liquid(solvent, T)
    return float(1.173e-16 * np.sqrt(18.0) * T / (mu * 34.0**0.6))
