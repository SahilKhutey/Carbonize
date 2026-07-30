"""
Physical constants and unit conversions
"""
from dataclasses import dataclass
from typing import Dict


R_GAS = 8.314462618            # J/(mol·K)
R_GAS_CAL = 1.987204          # cal/(mol·K)
AVOGADRO = 6.02214076e23       # 1/mol
BOLTZMANN = 1.380649e-23       # J/K
STEFAN_BOLTZMANN = 5.670374e-8  # W/(m²·K⁴)
FARADAY = 96485.33212          # C/mol
G_ACCEL = 9.80665              # m/s²


@dataclass(frozen=True)
class Conversions:
    """Unit conversion factors."""
    ATM_TO_PA = 101325.0
    BAR_TO_PA = 100000.0
    PSI_TO_PA = 6894.757
    MMHG_TO_PA = 133.322
    CAL_TO_J = 4.184
    BTU_TO_J = 1055.06
    HP_TO_W = 745.7
    KW_TO_HP = 1.34102
    GPM_TO_M3S = 6.30902e-5
    M3H_TO_M3S = 1.0 / 3600.0
    FT_TO_M = 0.3048
    LB_TO_KG = 0.453592


T_STANDARD = 273.15            # K
P_STANDARD = 101325.0          # Pa
T_NORMAL = 293.15              # K
P_NORMAL = 101325.0            # Pa


MOLAR_MASSES = {
    'H2': 2.016,
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'S': 32.065,
    'Hg': 200.59,
    'H2O': 18.015,
    'CO2': 44.009,
    'CO': 28.010,
    'CH4': 16.043,
    'NH3': 17.031,
    'H2S': 34.081,
    'SO2': 64.066,
    'SO3': 80.066,
    'NO': 30.006,
    'NO2': 46.006,
    'N2': 28.013,
    'O2': 31.999,
    'CaCO3': 100.087,
    'CaSO4': 136.14,
    'NaOH': 39.997,
    'MEA': 61.084,
    'MDEA': 119.163,
    'Piperazine': 86.136,
    'KS1': 396.0,
}


def get_molar_mass(compound: str) -> float:
    """Get molar mass of compound."""
    if compound in MOLAR_MASSES:
        return MOLAR_MASSES[compound]
    raise ValueError(f"Unknown compound: {compound}")


CRITICAL_PROPERTIES = {
    'CO2':  {'Tc': 304.13, 'Pc': 7.377e6, 'Vc': 9.4e-5, 'omega': 0.22394, 'Zc': 0.274},
    'H2O':  {'Tc': 647.10, 'Pc': 22.064e6, 'Vc': 5.6e-5, 'omega': 0.344, 'Zc': 0.229},
    'N2':   {'Tc': 126.19, 'Pc': 3.395e6, 'Vc': 8.95e-5, 'omega': 0.037, 'Zc': 0.289},
    'O2':   {'Tc': 154.58, 'Pc': 5.043e6, 'Vc': 7.34e-5, 'omega': 0.022, 'Zc': 0.288},
    'CH4':  {'Tc': 190.56, 'Pc': 4.599e6, 'Vc': 9.86e-5, 'omega': 0.011, 'Zc': 0.286},
    'H2S':  {'Tc': 373.30, 'Pc': 8.937e6, 'Vc': 9.85e-5, 'omega': 0.094, 'Zc': 0.284},
    'SO2':  {'Tc': 430.80, 'Pc': 7.884e6, 'Vc': 1.22e-4, 'omega': 0.256, 'Zc': 0.269},
    'MEA':  {'Tc': 678.0, 'Pc': 5.5e6, 'Vc': 1.97e-4, 'omega': 0.453, 'Zc': 0.193},
    'MDEA': {'Tc': 741.0, 'Pc': 4.0e6, 'Vc': 3.7e-4, 'omega': 0.794, 'Zc': 0.240},
}


def get_critical_properties(compound: str) -> Dict:
    """Get critical properties of compound."""
    if compound in CRITICAL_PROPERTIES:
        return CRITICAL_PROPERTIES[compound]
    raise ValueError(f"Unknown compound: {compound}")
