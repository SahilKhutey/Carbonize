"""
experimental_chemistry.py
Experimental Numba-accelerated chemical reaction kinetics solver for advance CCUS.
Supports:
  - NOx absorption & Calcium Nitrate fertilizer conversion
  - Magnesium carbonate substitution
  - Crosslinked chitosan matrix thermal deactivation protection

State Vector Units and Index Mapping (13 Species):
- y[0]: CO2_aq (mol/m³) - Dissolved carbon dioxide
- y[1]: HCO3 (mol/m³) - Bicarbonate ions
- y[2]: Ca2 (mol/m³) - Free calcium ions
- y[3]: CaCO3_s (mol/m³) - Calcium carbonate solid (calcite)
- y[4]: SO2_aq (mol/m³) - Dissolved sulfur dioxide
- y[5]: CaSO4_s (mol/m³) - Calcium sulfate solid (gypsum)
- y[6]: CA_active (mg/L) - Active Carbonic Anhydrase enzyme
- y[7]: Metal_chel (mol/m³) - Chelated heavy metals
- y[8]: PM_trapped (g/m³) - Trapped particulate matter
- y[9]: NOx_aq (mol/m³) - Dissolved NOx
- y[10]: CaNO3_s (mol/m³) - Calcium nitrate solid (fertilizer)
- y[11]: Mg2 (mol/m³) - Free magnesium ions
- y[12]: MgCO3_s (mol/m³) - Magnesium carbonate solid
"""

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp
from typing import Dict
from .config import CONFIG, R_GAS, STD_PRESSURE, MOLAR
from cbms_shared.constants import HENRY_CO2, HENRY_SO2, HENRY_NO2, KSP_CACO3, KSP_CASO4


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
    K_sp_caco3 = KSP_CACO3
    supersat_ca = (ca_free * hco3) / K_sp_caco3
    rate_caco3 = 1.5e-2 * ca_free * hco3 * (1.0 - 1.0 / supersat_ca) if supersat_ca > 1.0 else 0.0

    K_sp_mgco3 = 10.0
    supersat_mg = (mg_free * hco3) / K_sp_mgco3
    rate_mgco3 = 1.0e-2 * mg_free * hco3 * (1.0 - 1.0 / supersat_mg) if supersat_mg > 1.0 else 0.0

    dCa_dt = -rate_caco3
    dCaCO3_dt = rate_caco3
    dMg_dt = -rate_mgco3
    dMgCO3_dt = rate_mgco3

    # 4) SO2 absorption and gypsum precipitation (smoothed)
    H_so2 = HENRY_SO2
    dSO2_dt = k_so2 * (H_so2 * p_so2 - so2_aq)
    
    K_sp_caso4 = KSP_CASO4
    supersat_caso4 = (ca_free * so2_aq) / K_sp_caso4
    rate_caso4 = 5.0e-3 * ca_free * so2_aq * (1.0 - 1.0 / supersat_caso4) if supersat_caso4 > 1.0 else 0.0
    dSO2_dt -= rate_caso4
    dCa_dt -= rate_caso4
    dCaSO4_dt = rate_caso4

    # 5) Heavy metal chelation
    metal_inlet = 0.5
    free_amine_density = 0.05 * (1.0 - 0.25 * crosslinking_density)
    dMetal_dt = k_chel * free_amine_density * metal_inlet
    metal_chel_new = dMetal_dt

    # 6) Particulate matter capture
    pm_inlet = 25.0
    k_pm_cap = 0.18
    dPM_dt = k_pm_cap * pm_inlet * ca_active / 12.0

    # 7) NOx Absorption & Calcium Nitrate Fertilizer Precipitation
    H_nox = HENRY_NO2
    dNOx_dt = k_nox * (H_nox * p_nox - nox_aq)
    
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
        flow_nm3_per_hr: float = 10000.0,
        l_g_ratio: float = 8.5,
        superficial_velocity: float = 2.0,
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
        self.flow_nm3_hr = flow_nm3_per_hr
        self.l_g = l_g_ratio
        self.velocity = superficial_velocity
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

        H_co2 = HENRY_CO2
        H_so2 = HENRY_SO2
        H_nox = HENRY_NO2

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

        # Sizing & maintenance calculations
        actual_flow_m3_s = (self.flow_nm3_hr / 3600.0) * (self.T / 273.15)
        vessel_area = actual_flow_m3_s / self.velocity
        vessel_diameter = float(np.sqrt(4.0 * vessel_area / np.pi))
        vessel_height = float(self.velocity * self.tau)

        liquid_flow_m3_hr = float((self.flow_nm3_hr * self.l_g) / 1000.0)
        pump_flow_m3_s = liquid_flow_m3_hr / 3600.0
        pump_power = float((pump_flow_m3_s * 1000.0 * 9.81 * vessel_height) / (0.75 * 1000.0))

        reactor_vol = vessel_area * vessel_height
        caco3_mass_hr = (max(y_final[3], 0.0) / self.tau) * reactor_vol * 100.09 * 3.6
        caso4_mass_hr = (max(y_final[5], 0.0) / self.tau) * reactor_vol * 136.14 * 3.6
        mgco3_mass_hr = (max(y_final[12], 0.0) / self.tau) * reactor_vol * 84.31 * 3.6
        total_scaling_rate = float(caco3_mass_hr + caso4_mass_hr + mgco3_mass_hr)

        if total_scaling_rate > 1e-4:
            descaling_interval = float(5000.0 / (total_scaling_rate * 24.0))
            annual_downtime = float((365.0 / descaling_interval) * 36.0)
        else:
            descaling_interval = 365.0
            annual_downtime = 0.0
        adjusted_operating_hours = float(max(0.0, 8760.0 - annual_downtime))

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
            },
            "sizing": {
                "vessel_diameter_m": vessel_diameter,
                "vessel_height_m": vessel_height,
                "circulating_liquid_flow_m3_hr": liquid_flow_m3_hr,
                "pump_power_kw": pump_power,
                "descaling_interval_days": descaling_interval,
                "annual_downtime_hours": annual_downtime,
                "adjusted_operating_hours": adjusted_operating_hours,
                "total_scaling_rate_kg_hr": total_scaling_rate
            }
        }
