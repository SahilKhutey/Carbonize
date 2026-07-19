"""
Numba JIT-compiled kernels for the kinetics ODE.

State Vector Units and Index Mapping:
- y[0]: CO2_aq (mol/m³) - Dissolved carbon dioxide concentration
- y[1]: HCO3 (mol/m³) - Dissolved bicarbonate ion concentration
- y[2]: Ca2 (mol/m³) - Dissolved free calcium ion concentration
- y[3]: CaCO3_s (mol/m³) - Precipitated calcium carbonate solid concentration
- y[4]: SO2_aq (mol/m³) - Dissolved sulfur dioxide concentration
- y[5]: CaSO4_s (mol/m³) - Precipitated calcium sulfate solid concentration
- y[6]: CA_active (mg/L) - Active Carbonic Anhydrase enzyme concentration
- y[7]: Metal_chel (mol/m³) - Chelated heavy metal concentration
- y[8]: PM_trapped (g/m³) - Trapped particulate matter concentration
"""

from __future__ import annotations

import numpy as np
from numba import njit


from cbms_shared.constants import HENRY_SO2, KSP_CACO3, KSP_CASO4


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
    pm_inlet: float = 25.0,
    metal_inlet: float = 0.5,
    mesh_count: float = 6.0,
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
    K_sp = KSP_CACO3
    supersaturation = (ca_free * hco3) / K_sp
    k_precip = 1.5e-2
    if supersaturation > 1.0:
        rate_caco3 = k_precip * ca_free * hco3 * (1.0 - 1.0 / supersaturation)
    else:
        rate_caco3 = 0.0
    dCa_dt = -rate_caco3
    dCaCO3_dt = rate_caco3
    
    # 4) SO2 absorption and gypsum precipitation
    H_so2 = HENRY_SO2
    dSO2_dt = k_so2 * (H_so2 * p_so2 - so2_aq)
    
    K_sp_caso4 = KSP_CASO4
    supersat_caso4 = (ca_free * so2_aq) / K_sp_caso4
    if supersat_caso4 > 1.0:
        rate_caso4 = 5.0e-3 * ca_free * so2_aq * (1.0 - 1.0 / supersat_caso4)
    else:
        rate_caso4 = 0.0
    dSO2_dt -= rate_caso4
    dCa_dt -= rate_caso4
    dCaSO4_dt = rate_caso4
    
    # 5) Heavy metal chelation (Langmuir/saturable site depletion form)
    free_amine_density = 0.05
    dMetal_dt = k_chel * max(0.0, free_amine_density - metal_chel) * metal_inlet
    metal_chel_new = dMetal_dt
    
    # 6) Particulate matter capture (Saturable mesh filtration form)
    k_pm_cap = 0.18
    dPM_dt = k_pm_cap * max(0.0, pm_inlet - pm_cap) * (1.0 - np.exp(-mesh_count / 10.0)) * ca_active / 12.0
    
    return np.array([
        dCO2_dt, dHCO3_dt, dCa_dt, dCaCO3_dt,
        dSO2_dt, dCaSO4_dt, dCA_dt,
        metal_chel_new, dPM_dt
    ])


@njit(cache=True)
def compute_capture_efficiencies(
    initial_state: np.ndarray,
    final_state: np.ndarray,
    pm_inlet: float = 25.0,
    metal_inlet: float = 0.5,
) -> np.ndarray:
    """Compute per-pollutant capture efficiency percentages."""
    co2_in = max(initial_state[0], 1e-12)
    so2_in = max(initial_state[4], 1e-12)
    metal_in = max(metal_inlet, 1e-12)
    pm_in = max(pm_inlet, 1e-12)
    
    co2_pct = max(0.0, min(100.0, (co2_in - max(final_state[0], 0.0)) / co2_in * 100.0))
    so2_pct = max(0.0, min(100.0, (so2_in - max(final_state[4], 0.0)) / so2_in * 100.0))
    pm_pct = max(0.0, min(100.0, max(final_state[8], 0.0) / pm_in * 100.0))
    metal_pct = max(0.0, min(100.0, max(final_state[7], 0.0) / metal_in * 100.0))
    
    return np.array([co2_pct, so2_pct, pm_pct, metal_pct])

