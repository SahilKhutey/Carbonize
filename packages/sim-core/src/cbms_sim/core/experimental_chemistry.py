"""
experimental_chemistry.py
Experimental Numba-accelerated chemical reaction kinetics solver for advance CCUS.
Supports:
  - NOx absorption & Calcium Nitrate fertilizer conversion
  - Magnesium carbonate substitution
  - Crosslinked chitosan matrix thermal deactivation protection
"""

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp
from typing import Dict
from cbms_sim.core.config import CONFIG, R_GAS, STD_PRESSURE, MOLAR


@njit(cache=True, fastmath=True)
def reaction_rhs_experimental(
    t: float,
    y: np.ndarray,
    k_cat: float,
    K_M_co2: float,
    k_inact: float,
    E_a_inact: float,
    k_so2: float,
    k_chel: float,
    ph_initial: float,
    T_reactor: float,
    p_so2: float,
    p_nox: float,
    crosslinking_density: float,    # 0.0 to 1.0
    k_nox: float = 2.5e-2,
) -> np.ndarray:
    """
    RHS of the experimental 13-species kinetics ODE.

    State vector y (length 13):
        y[0] = [CO2_aq]      Dissolved CO2 [mol/m³]
        y[1] = [HCO3-]       Bicarbonate ion [mol/m³]
        y[2] = [Ca2+]        Free calcium ions [mol/m³]
        y[3] = [CaCO3_s]     Precipitated calcite [mol/m³]
        y[4] = [SO2_aq]      Dissolved SO2 [mol/m³]
        y[5] = [CaSO4_s]     Precipitated gypsum [mol/m³]
        y[6] = [CA_active]   Active enzyme [mg/L]
        y[7] = [Metal_chel]  Chelated trace metals [mol/m³]
        y[8] = [PM_trapped]  Particulate mass captured [kg/m³]
        y[9] = [NOx_aq]      Dissolved NOx [mol/m³]
        y[10] = [CaNO3_s]    Precipitated Calcium Nitrate [mol/m³]
        y[11] = [Mg2+]       Free magnesium ions [mol/m³]
        y[12] = [MgCO3_s]    Precipitated Magnesium Carbonate [mol/m³]
    """
    co2_aq = max(y[0], 0.0)
    hco3 = max(y[1], 0.0)
    ca_free = max(y[2], 0.0)
    caco3_s = max(y[3], 0.0)
    so2_aq = max(y[4], 0.0)
    caso4_s = max(y[5], 0.0)
    ca_active = max(y[6], 1e-9)
    metal_chel = max(y[7], 0.0)
    pm_cap = max(y[8], 0.0)
    nox_aq = max(y[9], 0.0)
    canitrate_s = max(y[10], 0.0)
    mg_free = max(y[11], 0.0)
    mgco3_s = max(y[12], 0.0)

    # 1) Enzyme thermal deactivation stabilized by chitosan crosslinking
    # High crosslinking density protects the enzyme from denaturation
    T_ref = 313.15
    k_inact_eff = k_inact * (1.0 - 0.5 * crosslinking_density)
    k_inact_T = k_inact_eff * np.exp(-E_a_inact / R_GAS * (1.0 / T_reactor - 1.0 / T_ref))
    dCA_dt = -k_inact_T * ca_active

    # 2) CO2 Hydration
    denom = (K_M_co2 * 1000.0) * (1.0 + hco3 / 26.0) + co2_aq
    v_cat = (k_cat * (ca_active / 30000.0) * co2_aq) / denom if denom > 1e-15 else 0.0
    dCO2_dt = -v_cat
    dHCO3_dt = v_cat

    # 3) Calcium & Magnesium Carbonate Precipitation
    # CaCO3
    K_sp_caco3 = 3.3e-9
    supersat_ca = (ca_free * hco3) / K_sp_caco3
    rate_caco3 = 1.5e-2 * ca_free * hco3 * (1.0 - 1.0 / supersat_ca) if supersat_ca > 1.0 else 0.0

    # MgCO3
    K_sp_mgco3 = 1.0e-5
    supersat_mg = (mg_free * hco3) / K_sp_mgco3
    rate_mgco3 = 1.0e-2 * mg_free * hco3 * (1.0 - 1.0 / supersat_mg) if supersat_mg > 1.0 else 0.0

    dCa_dt = -rate_caco3
    dCaCO3_dt = rate_caco3
    dMg_dt = -rate_mgco3
    dMgCO3_dt = rate_mgco3

    # 4) SO2 absorption and gypsum precipitation
    H_so2 = 1.2
    dSO2_dt = k_so2 * (H_so2 * p_so2 - so2_aq)
    
    K_sp_caso4 = 4.93e-5
    rate_caso4 = 5.0e-3 * ca_free * so2_aq if (ca_free * so2_aq) > K_sp_caso4 else 0.0
    dSO2_dt -= rate_caso4
    dCa_dt -= rate_caso4
    dCaSO4_dt = rate_caso4

    # 5) Heavy metal chelation (reduced by crosslinking density)
    metal_inlet = 0.5
    free_amine_density = 0.05 * (1.0 - 0.25 * crosslinking_density)
    dMetal_dt = k_chel * free_amine_density * metal_inlet
    metal_chel_new = dMetal_dt

    # 6) Particulate matter capture
    pm_inlet = 25.0
    k_pm_cap = 0.18
    dPM_dt = k_pm_cap * pm_inlet * ca_active / 12.0

    # 7) NOx Absorption & Calcium Nitrate Fertilizer Precipitation
    H_nox = 1.0e-2
    dNOx_dt = k_nox * (H_nox * p_nox - nox_aq)
    
    # 2 NOx_aq + Ca2+ -> Ca(NO3)2_s
    rate_canitrate = 4.0e-3 * ca_free * (nox_aq ** 2)
    dNOx_dt -= 2.0 * rate_canitrate
    dCa_dt -= rate_canitrate
    dCaNO3_dt = rate_canitrate

    return np.array([
        dCO2_dt, dHCO3_dt, dCa_dt, dCaCO3_dt,
        dSO2_dt, dCaSO4_dt, dCA_dt,
        metal_chel_new, dPM_dt,
        dNOx_dt, dCaNO3_dt, dMg_dt, dMgCO3_dt
    ])


class ExperimentalBiomineralizationSolver:
    """
    Experimental solver featuring NOx conversion, Mg substitution, and crosslinked chitosan matrix elements.
    """

    STATE_LABELS = [
        "CO2_aq", "HCO3-", "Ca2+", "CaCO3_s",
        "SO2_aq", "CaSO4_s", "CA_active", "Metal_chelated", "PM_trapped",
        "NOx_aq", "CaNO3_s", "Mg2+", "MgCO3_s"
    ]

    def __init__(
        self,
        co2_vol_pct: float,
        so2_mg_per_nm3: float,
        nox_inlet_ppm: float,
        ca_concentration_mg_l: float,
        calcium_source_g_per_l: float,
        crosslinking_density: float,     # 0.0 to 1.0
        mg_substitution_ratio: float,    # 0.0 to 1.0
        reactor_temperature_c: float = 40.0,
        residence_time_s: float = 27.0,
    ):
        self.co2_vol_pct = co2_vol_pct
        self.so2_mg_per_nm3 = so2_mg_per_nm3
        self.nox_ppm = nox_inlet_ppm
        self.ca_mg_l = ca_concentration_mg_l
        self.ca_source_g_l = calcium_source_g_per_l
        self.crosslinking = crosslinking_density
        self.mg_ratio = mg_substitution_ratio
        self.T = reactor_temperature_c + 273.15
        self.tau = residence_time_s

        # Convert inputs
        self.p_co2 = (co2_vol_pct / 100.0) * STD_PRESSURE
        self.p_so2 = so2_mg_per_nm3 * STD_PRESSURE / (MOLAR["SO2"] * 1e6)
        self.p_nox = (nox_inlet_ppm / 1e6) * STD_PRESSURE

        # Base cation loading
        total_cation_mol_m3 = (calcium_source_g_per_l * 1000.0) / 74.10
        self.ca_mol_m3 = total_cation_mol_m3 * (1.0 - mg_substitution_ratio)
        self.mg_mol_m3 = total_cation_mol_m3 * mg_substitution_ratio

        H_co2 = 3.4e-2
        H_so2 = 1.2
        H_nox = 1.0e-2

        self.y0 = np.array([
            H_co2 * self.p_co2,
            1.0,
            self.ca_mol_m3,
            0.0,
            H_so2 * self.p_so2,
            0.0,
            self.ca_mg_l,
            0.0,
            0.0,
            H_nox * self.p_nox,
            0.0,
            self.mg_mol_m3,
            0.0
        ])

    def run(self, rtol: float = 1e-8, atol: float = 1e-10) -> Dict:
        cfg = CONFIG.kinetics

        # Numba compilation warming
        _ = reaction_rhs_experimental(
            0.0, self.y0,
            cfg.k_cat, cfg.K_M_co2, cfg.k_inact, cfg.E_a_inact,
            cfg.k_so2_absorption, cfg.k_chelation,
            7.0, self.T, self.p_so2, self.p_nox, self.crosslinking
        )

        sol = solve_ivp(
            fun=lambda t, y: reaction_rhs_experimental(
                t, y,
                cfg.k_cat, cfg.K_M_co2, cfg.k_inact, cfg.E_a_inact,
                cfg.k_so2_absorption, cfg.k_chelation,
                7.0, self.T, self.p_so2, self.p_nox, self.crosslinking
            ),
            t_span=(0.0, self.tau),
            y0=self.y0,
            method="BDF",
            rtol=rtol,
            atol=atol,
        )

        if not sol.success:
            return {
                "success": False,
                "message": sol.message,
                "efficiencies": {"CO2": 0.0, "SO2": 0.0, "NOx": 0.0, "PM": 0.0, "Metal": 0.0},
                "block_strength_mpa": 0.0,
                "block_grade": "F",
                "final_state": {}
            }

        y_final = sol.y[:, -1]

        co2_in = max(self.y0[0], 1e-12)
        so2_in = max(self.y0[4], 1e-12)
        nox_in = max(self.y0[9], 1e-12)

        co2_pct = max(0.0, min(100.0, (self.y0[0] - max(y_final[0], 0.0)) / co2_in * 100.0))
        so2_pct = max(0.0, min(100.0, (self.y0[4] - max(y_final[4], 0.0)) / so2_in * 100.0))
        nox_pct = max(0.0, min(100.0, (self.y0[9] - max(y_final[9], 0.0)) / nox_in * 100.0))
        metal_pct = max(0.0, min(100.0, max(y_final[7], 0.0) / 0.5 * 100.0))
        pm_pct = max(0.0, min(100.0, max(y_final[8], 0.0) / 25.0 * 100.0))

        # Block strength with crosslinking density scaling
        base_strength = float(3.2 * np.log(1.0 + max(y_final[3], 0.0) + 1.2 * max(y_final[12], 0.0)))
        crosslinking_multiplier = 1.0 + 0.5 * self.crosslinking
        block_strength = float(base_strength * crosslinking_multiplier)

        # Grade criteria
        if block_strength >= 25.0:
            grade = "M25 (Premium)"
        elif block_strength >= 15.0:
            grade = "M15 (Standard)"
        elif block_strength >= 7.5:
            grade = "M7.5 (Low load)"
        else:
            grade = "Reject"

        return {
            "success": True,
            "message": sol.message,
            "efficiencies": {
                "CO2": float(co2_pct),
                "SO2": float(so2_pct),
                "NOx": float(nox_pct),
                "PM": float(pm_pct),
                "Metal": float(metal_pct)
            },
            "block_strength_mpa": block_strength,
            "block_grade": grade,
            "final_state": {
                label: float(y_final[i])
                for i, label in enumerate(self.STATE_LABELS)
            }
        }
