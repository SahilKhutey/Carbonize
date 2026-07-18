"""
core/block_strength.py
Predicts 48-hour compressive strength of composite blocks based on
pozzolanic aggregate ratio and hydraulic press compaction force.
"""

import numpy as np
from cbms_sim.core.config import CONFIG
from cbms_sim.core.mass_balance import MassBalanceResult


def predict_compressive_strength(
    mass_balance: MassBalanceResult,
    press_force_bar: float = 200.0,
    curing_hours: float = 48.0,
    temperature_c: float = 25.0,
) -> float:
    """
    Empirical model for composite block strength.

    Strength = alpha * (m_ash / m_CaCO3)^beta * ln(P_comp) * T_factor

    Args:
        mass_balance: Computed mass balance result
        press_force_bar: Hydraulic press compaction force
        curing_hours: Curing time before testing
        temperature_c: Ambient curing temperature

    Returns:
        Predicted compressive strength [MPa]
    """
    if mass_balance.caco3_output <= 0:
        return 0.0

    # Empirical fit constants (validated against lab data)
    alpha = 4.8
    beta = 0.42

    ash_ratio = mass_balance.fly_ash_captured / mass_balance.caco3_output
    ash_ratio = np.clip(ash_ratio, 0.01, 0.5)

    # Compaction contribution
    comp_factor = np.log(max(press_force_bar, 10.0))

    # Curing time contribution (logarithmic)
    cure_factor = np.log(1.0 + curing_hours / 24.0)

    # Temperature acceleration (Arrhenius-like)
    T_ref = 298.15  # 25°C
    T_actual = temperature_c + 273.15
    Ea = 35.0e3  # J/mol
    R = 8.314
    T_factor = np.exp(-Ea / R * (1.0 / T_actual - 1.0 / T_ref))

    # Chitosan lattice contribution
    chitosan_pct = (mass_balance.chitosan_lattice /
                    (mass_balance.caco3_output + mass_balance.fly_ash_captured))
    chitosan_factor = 1.0 + 0.6 * chitosan_pct

    strength = alpha * (ash_ratio ** beta) * comp_factor * cure_factor * T_factor * chitosan_factor
    return float(strength)


def classify_block_grade(strength_mpa: float) -> str:
    """
    Classify the composite block into Indian Standard (IS) grade.
    """
    if strength_mpa >= 25.0:
        return "M25 (Structural Concrete Equivalent)"
    elif strength_mpa >= 20.0:
        return "M20 (Load-Bearing Wall)"
    elif strength_mpa >= 10.0:
        return "M10 (Non-Load-Bearing Wall)"
    elif strength_mpa >= 5.0:
        return "IS 1077 Class A (Standard Brick)"
    elif strength_mpa >= 3.5:
        return "IS 2185 Grade A (Non-Load-Bearing Block)"
    else:
        return "Substandard — Requires Re-formulation"
