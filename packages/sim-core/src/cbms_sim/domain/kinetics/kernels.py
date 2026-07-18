"""Numba JIT-compiled kernels for the kinetics ODE."""

from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True, fastmath=True, boundscheck=False)
def reaction_rhs_numba(
    t: float,
    y: np.ndarray,
    k_cat: float,
    K_M_co2: float,
    k_inact: float,
    E_a_inact: float,
    k_so2: float,
    k_chel: float,
    ca_cl2: float,
    pH_initial: float,
    T_reactor: float,
    p_so2: float = 50.0,
) -> np.ndarray:
    """
    Right-hand side of the 9-species kinetics ODE.
    
    Implements the multi-pollutant reaction kinetics for the
    biomineralization capture system.
    
    References:
        - Mirjafari et al. 2007 (CA kinetics)
        - Rigkos et al. 2024 (thermostable CA)
    """
    # Ensure non-negative concentrations
    co2_aq = max(y[0], 0.0)
    hco3 = max(y[1], 0.0)
    ca_free = max(y[2], 0.0)
    caco3_s = max(y[3], 0.0)
    so2_aq = max(y[4], 0.0)
    caso4_s = max(y[5], 0.0)
    ca_active = max(y[6], 1e-9)
    metal_chel = max(y[7], 0.0)
    pm_cap = max(y[8], 0.0)
    
    # 1) Enzyme thermal deactivation (Arrhenius)
    T_ref = 313.15  # 40°C
    k_inact_T = k_inact * np.exp(-E_a_inact / 8.314 * (1.0 / T_reactor - 1.0 / T_ref))
    dCA_dt = -k_inact_T * ca_active
    
    # 2) CO2 hydration (Michaelis-Menten with product inhibition)
    K_M_eff = K_M_co2 * 1000.0 * (1.0 + hco3 / 26.0)
    denom = K_M_eff + co2_aq
    v_cat = (k_cat * (ca_active / 30000.0) * co2_aq) / denom if denom > 1e-15 else 0.0
    dCO2_dt = -v_cat
    dHCO3_dt = v_cat
    
    # 3) CaCO3 precipitation
    K_sp = 3.3e-9
    supersaturation = (ca_free * hco3) / K_sp
    k_precip = 1.5e-2
    if supersaturation > 1.0:
        rate_caco3 = k_precip * ca_free * hco3 * (1.0 - 1.0 / supersaturation)
    else:
        rate_caco3 = 0.0
    dCa_dt = -rate_caco3
    dCaCO3_dt = rate_caco3
    
    # 4) SO2 absorption and gypsum precipitation
    H_so2 = 1.2
    dSO2_dt = k_so2 * (H_so2 * p_so2 - so2_aq)
    
    K_sp_caso4 = 4.93e-5
    if (ca_free * so2_aq) > K_sp_caso4:
        rate_caso4 = 5.0e-3 * ca_free * so2_aq
    else:
        rate_caso4 = 0.0
    dSO2_dt -= rate_caso4
    dCa_dt -= rate_caso4
    dCaSO4_dt = rate_caso4
    
    # 5) Heavy metal chelation
    metal_inlet = 0.5
    free_amine_density = 0.05
    dMetal_dt = k_chel * free_amine_density * metal_inlet
    metal_chel_new = dMetal_dt
    
    # 6) Particulate matter capture
    pm_inlet = 25.0
    k_pm_cap = 0.18
    dPM_dt = k_pm_cap * pm_inlet * ca_active / 12.0
    
    return np.array([
        dCO2_dt, dHCO3_dt, dCa_dt, dCaCO3_dt,
        dSO2_dt, dCaSO4_dt, dCA_dt,
        metal_chel_new, dPM_dt
    ])


@njit(cache=True)
def compute_capture_efficiencies(
    initial_state: np.ndarray,
    final_state: np.ndarray,
) -> np.ndarray:
    """Compute per-pollutant capture efficiency percentages."""
    co2_in = max(initial_state[0], 1e-12)
    so2_in = max(initial_state[4], 1e-12)
    metal_in = 0.5
    pm_in = 25.0
    
    co2_pct = max(0.0, min(100.0, (co2_in - max(final_state[0], 0.0)) / co2_in * 100.0))
    so2_pct = max(0.0, min(100.0, (so2_in - max(final_state[4], 0.0)) / so2_in * 100.0))
    pm_pct = max(0.0, min(100.0, max(final_state[8], 0.0) / pm_in * 100.0))
    metal_pct = max(0.0, min(100.0, max(final_state[7], 0.0) / metal_in * 100.0))
    
    return np.array([co2_pct, so2_pct, pm_pct, metal_pct])
