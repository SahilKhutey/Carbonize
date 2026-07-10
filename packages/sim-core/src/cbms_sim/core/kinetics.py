"""
core/kinetics.py
Non-linear reaction kinetics solver for the biomineralization reactor.

Implements the enzyme-catalyzed CO2 hydration pathway coupled with
chitosan matrix sol-gel transition dynamics. Uses scipy.integrate.solve_ivp
with the BDF stiff solver for numerical stability.
"""

import numpy as np
from scipy.integrate import solve_ivp
from numba import njit
from typing import Tuple, Dict
from core.config import CONFIG, R_GAS, STD_TEMP


# ============================================================
# NUMBA-ACCELERATED RHS FUNCTION
# ============================================================
@njit(cache=True, fastmath=True)
def _reaction_rhs_numba(
    t: float,
    y: np.ndarray,
    k_cat: float,
    K_M_co2: float,
    k_inact: float,
    E_a_inact: float,
    k_so2: float,
    k_chel: float,
    ca_cl2: float,
    ph_initial: float,
    T_reactor: float,
) -> np.ndarray:
    """
    Right-hand side of the coupled ODE system for in-tower reactions.

    State vector y (length 9):
        y[0] = [CO2_aq]      Dissolved CO2 [mol/m³]
        y[1] = [HCO3-]       Bicarbonate ion [mol/m³]
        y[2] = [Ca2+]        Free calcium ions [mol/m³]
        y[3] = [CaCO3_s]     Precipitated calcite/aragonite [mol/m³]
        y[4] = [SO2_aq]      Dissolved SO2 [mol/m³]
        y[5] = [CaSO4_s]     Precipitated gypsum [mol/m³]
        y[6] = [CA_active]   Active enzyme concentration [mg/L]
        y[7] = [Heavy_metal_chelated]  [mol/m³]
        y[8] = [PM_trapped]  Particulate mass captured [kg/m³]

    Returns dy/dt vector of the same shape.
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

    # --------------------------------------------------
    # 1) ENZYME THERMAL DEACTIVATION (first-order)
    # --------------------------------------------------
    # Arrhenius: k_inact(T) = k_inact_ref * exp(-Ea/R * (1/T - 1/T_ref))
    T_ref = 313.15  # 40°C reference
    k_inact_T = k_inact * np.exp(-E_a_inact / R_GAS * (1.0/T_reactor - 1.0/T_ref))
    dCA_dt = -k_inact_T * ca_active

    # --------------------------------------------------
    # 2) CO2 HYDRATION (Michaelis-Menten with carbonic anhydrase)
    # --------------------------------------------------
    # Rate limited by enzyme catalysis; product inhibition by HCO3-
    v_cat = (k_cat * ca_active * co2_aq) / (K_M_co2 * (1.0 + hco3 / 26.0) + co2_aq)
    dCO2_dt = -v_cat
    dHCO3_dt = v_cat

    # --------------------------------------------------
    # 3) CALCIUM CARBONATE PRECIPITATION
    # --------------------------------------------------
    # Nucleation is enhanced by chitosan matrix presence (template effect)
    # Simplified: rate proportional to supersaturation index
    K_sp_caco3 = 3.3e-9  # Solubility product at 25°C
    supersaturation = (ca_free * hco3) / K_sp_caco3
    k_precip = 1.5e-2  # Tunable precipitation rate constant
    if supersaturation > 1.0:
        rate_caco3 = k_precip * ca_free * hco3 * (1.0 - 1.0 / supersaturation)
    else:
        rate_caco3 = 0.0

    dCa_dt = -rate_caco3
    dCaCO3_dt = rate_caco3

    # --------------------------------------------------
    # 4) SO2 ABSORPTION (alkaline dissolution)
    # --------------------------------------------------
    # Henry's law at reactor T; alkaline pH drives absorption
    H_so2 = 1.2  # mol/(m³·Pa), approximate
    p_so2 = 50.0  # Partial pressure [Pa] of SO2 in flue gas
    dSO2_dt = k_so2 * (H_so2 * p_so2 - so2_aq)

    # Gypsum precipitation
    K_sp_caso4 = 4.93e-5
    if (ca_free * so2_aq) > K_sp_caso4:
        rate_caso4 = 5.0e-3 * ca_free * so2_aq
    else:
        rate_caso4 = 0.0
    dSO2_dt -= rate_caso4
    dCa_dt -= rate_caso4
    dCaSO4_dt = rate_caso4

    # --------------------------------------------------
    # 5) HEAVY METAL CHELATION
    # --------------------------------------------------
    # Pseudo-first-order, dependent on free amine density
    # Inlet heavy metal concentration: assume trace [mol/m³]
    metal_inlet = 0.5  # [mol/m³] typical industrial Hg/Pb/Cd
    free_amine_density = 0.05  # [mol/m³] accessible amine sites
    dMetal_dt = k_chel * free_amine_density * metal_inlet - 0.0  # Effectively sink
    metal_chel_new = dMetal_dt

    # --------------------------------------------------
    # 6) PARTICULATE MATTER CAPTURE (viscous occlusion)
    # --------------------------------------------------
    # First-order electrostatic capture by protonated chitosan
    pm_inlet = 25.0  # [g/m³] typical PM2.5/10 load
    k_pm_cap = 0.18  # [m³/(g·s)]
    dPM_dt = k_pm_cap * pm_inlet * ca_active / 12.0  # Scaled by enzyme proxy

    # Return dy/dt array of length 9
    return np.array([
        dCO2_dt, dHCO3_dt, dCa_dt, dCaCO3_dt,
        dSO2_dt, dCaSO4_dt, dCA_dt,
        metal_chel_new, dPM_dt
    ])


# ============================================================
# HIGH-LEVEL SOLVER
# ============================================================
class BiomineralizationSolver:
    """
    Solves the coupled reaction kinetics for the Stage 3 tower.

    Usage:
        solver = BiomineralizationSolver(
            co2_partial_pressure_pa=14000.0,  # 14% vol
            so2_partial_pressure_pa=50.0,
            residence_time_s=27.0,
            ca_concentration_mg_l=12.0,
            calcium_source_mol_m3=850.0,
        )
        result = solver.run()
    """

    STATE_LABELS = [
        "CO2_aq", "HCO3-", "Ca2+", "CaCO3_s",
        "SO2_aq", "CaSO4_s", "CA_active", "Metal_chelated", "PM_trapped"
    ]

    def __init__(
        self,
        co2_partial_pressure_pa: float,
        so2_partial_pressure_pa: float,
        residence_time_s: float,
        ca_concentration_mg_l: float,
        calcium_source_mol_m3: float,
        reactor_temperature_k: float = 313.15,
    ):
        self.p_co2 = co2_partial_pressure_pa
        self.p_so2 = so2_partial_pressure_pa
        self.tau = residence_time_s
        self.ca_mg_l = ca_concentration_mg_l
        self.ca_mol_m3 = calcium_source_mol_m3
        self.T = reactor_temperature_k

        # Initial conditions (mol/m³, except CA in mg/L)
        # Henry's law to compute initial dissolved CO2/SO2
        H_co2 = 3.4e-2  # mol/(m³·Pa)
        self.y0 = np.array([
            H_co2 * self.p_co2,    # CO2_aq initial
            1.0,                    # HCO3- background
            self.ca_mol_m3,         # Ca2+
            0.0,                    # CaCO3_s
            1.2 * self.p_so2,       # SO2_aq initial
            0.0,                    # CaSO4_s
            self.ca_mg_l,           # CA_active
            0.0,                    # metal_chelated
            0.0,                    # PM_trapped
        ])

    def run(self, rtol: float = 1e-8, atol: float = 1e-10) -> Dict:
        """
        Execute the ODE integration and return derived metrics.

        Returns:
            dict with keys:
                - co2_capture_efficiency_pct
                - so2_capture_efficiency_pct
                - pm_capture_efficiency_pct
                - metal_chelation_pct
                - enzyme_deactivation_pct
                - final_state: Dict[str, float]
                - solver_success: bool
        """
        cfg = CONFIG.kinetics

        # Warmup: compile numba
        _ = _reaction_rhs_numba(
            0.0, self.y0,
            cfg.k_cat, cfg.K_M_co2, cfg.k_inact, cfg.E_a_inact,
            cfg.k_so2_absorption, cfg.k_chelation,
            self.ca_mol_m3, 7.0, self.T
        )

        sol = solve_ivp(
            fun=lambda t, y: _reaction_rhs_numba(
                t, y,
                cfg.k_cat, cfg.K_M_co2, cfg.k_inact, cfg.E_a_inact,
                cfg.k_so2_absorption, cfg.k_chelation,
                self.ca_mol_m3, 7.0, self.T
            ),
            t_span=(0.0, self.tau),
            y0=self.y0,
            method="BDF",          # Implicit stiff solver
            rtol=rtol,
            atol=atol,
            dense_output=True,
        )

        if not sol.success:
            return {
                "solver_success": False,
                "solver_message": sol.message,
                "co2_capture_efficiency_pct": 0.0,
                "so2_capture_efficiency_pct": 0.0,
                "pm_capture_efficiency_pct": 0.0,
                "metal_chelation_pct": 0.0,
                "enzyme_deactivation_pct": 0.0,
                "final_state": {},
            }

        y_final = sol.y[:, -1]

        # Compute capture efficiencies
        co2_inlet = self.y0[0] + 1e-12
        so2_inlet = self.y0[4] + 1e-12

        co2_consumed = max(self.y0[0] - y_final[0], 0.0)
        so2_consumed = max(self.y0[4] - y_final[4], 0.0)
        ca_deact = max(self.y0[6] - y_final[6], 0.0)
        metal_chel = y_final[7]
        pm_cap = y_final[8]

        result = {
            "solver_success": True,
            "solver_message": sol.message,
            "co2_capture_efficiency_pct": float(min(100.0, (co2_consumed / co2_inlet) * 100.0)),
            "so2_capture_efficiency_pct": float(min(100.0, (so2_consumed / so2_inlet) * 100.0)),
            "metal_chelation_pct": float(min(100.0, (metal_chel / 0.5) * 100.0)),
            "pm_capture_efficiency_pct": float(min(100.0, pm_cap / 25.0 * 100.0)),
            "enzyme_deactivation_pct": float((ca_deact / self.y0[6]) * 100.0),
            "final_state": {
                label: float(y_final[i])
                for i, label in enumerate(self.STATE_LABELS)
            },
            "solution_time_s": float(sol.t[-1]),
            "nfev": int(sol.nfev),
            "njev": int(sol.njev),
        }
        return result


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================
def solve_reactor_kinetics(
    co2_vol_pct: float = 14.0,
    so2_mg_per_nm3: float = 1200.0,
    flow_nm3_per_hr: float = 10000.0,
    enzyme_mg_per_l: float = 12.0,
    calcium_source_g_per_l: float = 35.0,
    reactor_temp_c: float = 40.0,
) -> Dict:
    """
    High-level wrapper translating industrial plant inputs to solver.

    Args:
        co2_vol_pct: CO2 concentration in flue gas [vol%]
        so2_mg_per_nm3: SO2 concentration [mg/Nm³]
        flow_nm3_per_hr: Volumetric exhaust flow [Nm³/hr]
        enzyme_mg_per_l: Initial CA enzyme concentration [mg/L]
        calcium_source_g_per_l: Ca²⁺ source concentration [g/L as Ca(OH)2 equiv]
        reactor_temp_c: Reactor operating temperature [°C]

    Returns:
        Capture efficiency metrics dict
    """
    from core.config import MOLAR, STD_PRESSURE

    # Convert to SI partial pressures
    p_co2 = (co2_vol_pct / 100.0) * STD_PRESSURE
    p_so2 = so2_mg_per_nm3 * STD_PRESSURE / (MOLAR["SO2"] * 1e6)  # Pa

    # Calcium source in mol/m³ (from g/L)
    # 1 g/L Ca(OH)2 = 1000 g/m³ / 74.1 g/mol = 13.49 mol/m³
    ca_mol_m3 = calcium_source_g_per_l * 1000.0 / 74.10

    solver = BiomineralizationSolver(
        co2_partial_pressure_pa=p_co2,
        so2_partial_pressure_pa=p_so2,
        residence_time_s=CONFIG.geometry.RESIDENCE_TIME,
        ca_concentration_mg_l=enzyme_mg_per_l,
        calcium_source_mol_m3=ca_mol_m3,
        reactor_temperature_k=reactor_temp_c + 273.15,
    )

    return solver.run()
