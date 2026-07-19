"""
Extended kinetics engine with explicit multi-gas competition.

Models CO₂, SO₂, and NOₓ absorption in a shared alkaline slurry,
capturing:
- Alkalinity budget depletion
- Ca²⁺ competition for precipitation
- pH-driven CA activity loss
- Chitosan site competition (metals vs. CO₂)

State Vector Units and Index Mapping (17 Species):
- y[0]: CO2_aq (mol/m³) - Dissolved carbon dioxide
- y[1]: HCO3 (mol/m³) - Bicarbonate ions
- y[2]: CO3 (mol/m³) - Carbonate ions
- y[3]: Ca2 (mol/m³) - Free calcium ions
- y[4]: CaCO3_s (mol/m³) - Calcium carbonate solid (calcite)
- y[5]: SO2_aq (mol/m³) - Dissolved sulfur dioxide
- y[6]: HSO3 (mol/m³) - Bisulfite ions
- y[7]: SO3 (mol/m³) - Sulfite ions
- y[8]: SO4 (mol/m³) - Sulfate ions
- y[9]: CaSO3_s (mol/m³) - Calcium sulfite solid
- y[10]: CaSO4_s (mol/m³) - Calcium sulfate solid (gypsum)
- y[11]: NO2_aq (mol/m³) - Dissolved nitrogen dioxide (NOx surrogate)
- y[12]: NO3 (mol/m³) - Nitrate ions
- y[13]: H_plus (mol/m³) - Hydronium (H+) ions
- y[14]: CA_active (mg/L) - Active Carbonic Anhydrase enzyme
- y[15]: Metal_chel (mol/m³) - Chelated heavy metals
- y[16]: PM_trapped (g/m³) - Trapped particulate matter

[!] PHYSICAL SIMPLIFICATION NOTICE:
NOx is modeled using NO2_aq as a surrogate with a simplified diprotic acid-like dissociation
framework (analogous to SO2). In real flue-gas environments, NOx consists predominantly of NO
(which has extremely low aqueous solubility) and NO2 disproportionates complexly into HNO3 and HNO2.
This model assumes flue-gas pre-oxidation of NO to NO2 to enable capture. Validate absorption
efficiencies against wet FGD literature for specific flue-gas compositions.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
import numpy as np
from numba import njit
from scipy.integrate import solve_ivp

from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.models.results import KineticsResult
from cbms_shared.constants import MOLAR_MASSES, HENRY_CO2, HENRY_SO2, HENRY_NO2, KSP_CACO3, KSP_CASO4, KSP_CASO3
from cbms_shared.exceptions import NumericalDivergenceError
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


@njit(cache=True, fastmath=True)
def extended_rhs_numba(
    t, y, k_cat, K_M_co2, K_i_hco3,
    k_so2_abs, K_so2_dissociation,
    k_no2_abs, K_no2_dissociation,
    k_sulfite_oxidation,
    k_precip_caco3, k_precip_caso3, k_precip_caso4,
    Ksp_caco3, Ksp_caso4, Ksp_caso3,
    k_chel, free_amine_density,
    pm_inlet, k_pm_cap,
    ca_inactivation, E_a_inact, T_reactor,
    R_gas=8.314, T_ref=313.15,
    p_co2=14000.0, p_so2=50.0, p_no2=20.0,  # Pa
    metal_inlet=0.5, mesh_count=6.0,
    liquid_to_gas_ratio=8.5,
):
    """
    Right-hand side for extended multi-species kinetics ODE.
    
    All three acidic gases compete for the same alkalinity budget
    and Ca²⁺ pool. The pH is computed from total alkalinity, which
    is conserved (modulo buffer additions).
    """
    
    # Ensure non-negative concentrations
    y_safe = np.zeros(17)
    for i in range(17):
        y_safe[i] = max(y[i], 0.0)
    
    # Unpack state
    CO2_aq = y_safe[0]
    HCO3 = y_safe[1]
    CO3 = y_safe[2]
    Ca2 = y_safe[3]
    CaCO3_s = y_safe[4]
    SO2_aq = y_safe[5]
    HSO3 = y_safe[6]
    SO3 = y_safe[7]
    SO4 = y_safe[8]
    CaSO3_s = y_safe[9]
    CaSO4_s = y_safe[10]
    NO2_aq = y_safe[11]
    NO3 = y_safe[12]
    H_plus = max(y_safe[13], 1e-10)  # Avoid log(0)
    CA_active = max(y_safe[14], 1e-9)
    Metal_chel = y_safe[15]
    PM_trapped = y_safe[16]
    
    # pH effect on CA activity
    pH = -np.log10(H_plus)
    if pH < 7.0:
        pH_factor = 10 ** (pH - 7.0)
    else:
        pH_factor = 1.0
    
    # Michaelis-Menten with product inhibition
    denom = K_M_co2 * (1.0 + HCO3 / K_i_hco3) + CO2_aq
    v_cat = (k_cat * (CA_active / 30000.0) * CO2_aq) / denom * pH_factor if denom > 1e-15 else 0.0
    
    # SO₂ absorption
    H_SO2_inv = HENRY_SO2
    SO2_eq = H_SO2_inv * p_so2
    k_so2_eff = k_so2_abs * (1.0 + 0.1 * HCO3 / H_plus)
    v_so2_abs = k_so2_eff * (SO2_eq - SO2_aq)
    if v_so2_abs < 0.0:
        v_so2_abs = 0.0
    
    # NO₂ absorption
    H_NO2_inv = HENRY_NO2
    NO2_eq = H_NO2_inv * p_no2
    v_no2_abs = k_no2_abs * (NO2_eq - NO2_aq)
    if v_no2_abs < 0.0:
        v_no2_abs = 0.0
    
    # Fast protonation/dissociation reactions (modeled kinetics-style)
    k_fast = 100.0  # Fast rate constant
    
    # 1) Carbonate dissociation: HCO3- <-> CO3(2-) + H+ (pKa2 = 10.33)
    v_carb_diss = k_fast * (HCO3 - H_plus * CO3 / 10**-10.33)
    
    # 2) Sulfite dissociation: HSO3- <-> SO3(2-) + H+ (pKa2 = 7.2)
    v_sulf_diss = k_fast * (HSO3 - H_plus * SO3 / 10**-7.2)
    
    # 3) SO2 dissociation: SO2_aq <-> HSO3- + H+
    v_so2_diss = k_fast * (SO2_aq - H_plus * HSO3 / K_so2_dissociation)
    
    # 4) NO2 dissociation: NO2_aq <-> NO3- + H+
    v_no2_diss = k_fast * (NO2_aq - H_plus * NO3 / K_no2_dissociation)
    
    # Sulfite -> sulfate oxidation
    v_sulfite_ox = k_sulfite_oxidation * SO3 * 21.0
    
    # CaCO₃ precipitation
    SI_caco3 = (Ca2 * CO3) / Ksp_caco3
    if SI_caco3 > 1.0:
        r_caco3 = k_precip_caco3 * Ca2 * CO3 * (1.0 - 1.0 / SI_caco3) * 2.5
    else:
        r_caco3 = 0.0
    
    # CaSO₃ precipitation
    SI_caso3 = (Ca2 * SO3) / Ksp_caso3
    if SI_caso3 > 1.0:
        r_caso3 = k_precip_caso3 * Ca2 * SO3 * (1.0 - 1.0 / SI_caso3)
    else:
        r_caso3 = 0.0
    
    # CaSO₄ precipitation
    SI_caso4 = (Ca2 * SO4) / Ksp_caso4
    if SI_caso4 > 1.0:
        r_caso4 = k_precip_caso4 * Ca2 * SO4 * (1.0 - 1.0 / SI_caso4)
    else:
        r_caso4 = 0.0
    
    # Total Ca²⁺ consumption
    r_ca_total = r_caco3 + r_caso3 + r_caso4
    
    # Heavy metal chelation (unit-consistent)
    # metal_inlet is in mg/Nm3 of gas
    # liquid_to_gas_ratio is in L/Nm3
    # Molar mass of heavy metal is ~200.0 g/mol
    # Convert mg/Nm3 gas to mol/m3 liquid:
    metal_liq_total = metal_inlet / (liquid_to_gas_ratio * 200.0)
    Metal_free = max(0.0, metal_liq_total - Metal_chel)
    
    pH_chel_factor = 1.0 / (1.0 + np.exp(-(pH - 5.5) * 3.0))
    co2_competition = 1.0 / (1.0 + 0.1 * CO2_aq)
    v_chel = k_chel * max(0.0, free_amine_density - Metal_chel) * Metal_free * pH_chel_factor * co2_competition
    
    # Enzyme deactivation
    k_inact_T = ca_inactivation * np.exp(
        -E_a_inact / R_gas * (1.0 / T_reactor - 1.0 / T_ref)
    )
    if pH < 5.5:
        pH_denat = 1e-3 * (5.5 - pH)
    else:
        pH_denat = 0.0
    
    # PM capture (saturable mesh filtration form)
    v_pm = k_pm_cap * max(0.0, pm_inlet - PM_trapped) * (1.0 - np.exp(-mesh_count / 10.0)) * CA_active / 12.0

    # ODE outputs
    dydt = np.zeros(17)
    dydt[0] = -v_cat
    dydt[1] = v_cat - v_carb_diss
    dydt[2] = v_carb_diss - r_caco3
    dydt[3] = -r_ca_total
    dydt[4] = r_caco3
    dydt[5] = v_so2_abs - v_so2_diss
    dydt[6] = v_so2_diss - v_sulf_diss
    dydt[7] = v_sulf_diss - v_sulfite_ox - r_caso3
    dydt[8] = v_sulfite_ox - r_caso4
    dydt[9] = r_caso3
    dydt[10] = r_caso4
    dydt[11] = v_no2_abs - v_no2_diss
    dydt[12] = v_no2_diss
    
    # Buffered pH tracking:
    # d[H+]/dt = H_plus * ln(10) / beta * (H_production - H_consumption)
    # where beta is the buffer capacity in mol/m³ (mM).
    # Default buffer capacity: 50.0 mM (mol/m³)
    beta = 50.0
    H_production = v_cat + v_so2_diss + v_no2_diss
    H_consumption = 2.0 * r_caco3 + 2.0 * r_caso3
    dydt[13] = H_plus * np.log(10) / beta * (H_production - H_consumption)
    
    # CA inactivation
    dydt[14] = -k_inact_T * CA_active - pH_denat * CA_active
    
    # Metal chelation
    dydt[15] = v_chel
    
    # PM trapping
    dydt[16] = v_pm
    
    return dydt


@dataclass(frozen=True)
class ExtendedKineticsConfig:
    """Extended solver config."""
    method: str = "BDF"
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step_s: float = 0.1


class ExtendedKineticsEngine:
    """Reaction kinetics solver with multi-gas competition."""
    
    def __init__(self, config: ExtendedKineticsConfig | None = None) -> None:
        self.config = config or ExtendedKineticsConfig()
        self._warmed_up = False
        
    def warmup(self) -> None:
        if self._warmed_up:
            return
        y_dummy = np.zeros(17)
        y_dummy[0] = 1.0
        y_dummy[1] = 1.0
        y_dummy[3] = 100.0
        y_dummy[13] = 10**-8.5
        y_dummy[14] = 12.0
        _ = extended_rhs_numba(
            0.0, y_dummy,
            k_cat=1.0e6, K_M_co2=8.5, K_i_hco3=26.0,
            k_so2_abs=2.5e-2, K_so2_dissociation=10**-1.85,
            k_no2_abs=1.0e-2, K_no2_dissociation=10**-1.4,
            k_sulfite_oxidation=1.0e-4,
            k_precip_caco3=1.5e-2, k_precip_caso3=1.0e-2, k_precip_caso4=5.0e-3,
            Ksp_caco3=KSP_CACO3, Ksp_caso4=KSP_CASO4, Ksp_caso3=KSP_CASO3,
            k_chel=8.0e-3, free_amine_density=0.05, metal_inlet=0.5,
            pm_inlet=25.0, k_pm_cap=0.18, mesh_count=6.0,
            ca_inactivation=5.0e-5, E_a_inact=85.0e3, T_reactor=313.15
        )
        self._warmed_up = True
        
    def solve(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions,
        residence_time_s: float = 27.0,
    ) -> KineticsResult:
        if not self._warmed_up:
            self.warmup()
            
        start_time = time.perf_counter()
        
        # Initial conditions
        y0 = self._compute_initial_conditions(plant, reagent, conditions)
        
        # Compute gas partial pressures
        p_co2 = float(plant.co2_vol_pct) / 100.0 * 101325.0
        p_so2 = float(plant.so2_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["SO2"] * 1e6)
        p_no2 = float(plant.nox_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["NO2"] * 1e6)

        pm_inlet = float(plant.fly_ash_g_per_nm3)
        metal_inlet = sum(float(m.get("conc_ug_per_nm3", 0.0)) for m in plant.heavy_metal_profile) / 1000.0
        if metal_inlet <= 0.0:
            metal_inlet = 0.5
        if pm_inlet <= 0.0:
            pm_inlet = 25.0
        mesh_count = float(conditions.mesh_count)

        # Derive free amine density (mol/m3 of liquid) from chitosan wt% and density
        # chitosan_wt is fractional weight of chitosan in slurry
        chitosan_wt = float(reagent.chitosan_wt_pct) / 100.0
        # Slurry density is assumed to be 1010 g/L (kg/m3)
        chitosan_conc_g_l = chitosan_wt * 1010.0
        # Glucosamine repeating unit (M = 161.16 g/mol) N-acetylglucosamine (M = 203.19 g/mol)
        # Assuming Degree of Deacetylation (DDA) is 85% (0.85)
        # Average molar mass of repeating unit: M_unit = 0.85 * 161.16 + 0.15 * 203.19 = 167.46 g/mol
        # Amine site density: 0.85 / 167.46 = 5.08 mmol/g of chitosan.
        # free_amine_density (mol/m3) = chitosan_conc_g_l * 5.08 mmol/g = chitosan_conc_g_l * (0.85 / 167.46) * 1000.0
        free_amine_density = chitosan_conc_g_l * (0.85 / 167.46) * 1000.0

        liquid_to_gas_ratio = float(conditions.liquid_to_gas_ratio)

        # Solver parameters
        solver_params = (
            1.0e6,  # k_cat
            8.5,    # K_M_co2
            26.0,   # K_i_hco3
            2.5e-2,  # k_so2_abs
            10**-1.85, # K_so2_dissociation
            1.0e-2,  # k_no2_abs
            10**-1.4,  # K_no2_dissociation
            1.0e-4,  # k_sulfite_oxidation
            1.5e-2,  # k_precip_caco3
            1.0e-2,  # k_precip_caso3
            5.0e-3,  # k_precip_caso4
            KSP_CACO3,  # Ksp_caco3
            KSP_CASO4,  # Ksp_caso4
            KSP_CASO3,  # Ksp_caso3
            8.0e-3,  # k_chel
            free_amine_density,  # free_amine_density (mol/m3)
            pm_inlet,
            0.18,    # k_pm_cap
            5.0e-5,  # ca_inactivation
            85.0e3,  # E_a_inact
            float(conditions.reactor_temp_c) + 273.15,
            8.314,   # R_gas
            313.15,  # T_ref
            p_co2,   # p_co2
            p_so2,   # p_so2
            p_no2,   # p_no2
            metal_inlet,
            mesh_count,
            liquid_to_gas_ratio,
        )
        
        sol = solve_ivp(
            fun=lambda t, y: extended_rhs_numba(t, y, *solver_params),
            t_span=(0.0, float(residence_time_s)),
            y0=y0,
            method=self.config.method,
            rtol=self.config.rtol,
            atol=self.config.atol,
            max_step=self.config.max_step_s,
            dense_output=True,
        )
        
        if not sol.success:
            raise NumericalDivergenceError(
                f"Extended kinetics solver failed: {sol.message}",
                nfev=int(sol.nfev),
                final_time=float(sol.t[-1]),
            )
            
        t_uniform = np.linspace(0, residence_time_s, 1000)
        y_uniform = sol.sol(t_uniform)
        
        # Efficiencies calculation
        co2_in = max(y0[0], 1e-12)
        so2_in = max(y0[5], 1e-12)
        nox_in = max(y0[11], 1e-12)
        # Convert metal inlet (mg/Nm3) to liquid molar loading (mol/m3)
        metal_liq_total = metal_inlet / (liquid_to_gas_ratio * 200.0)
        metal_in = max(metal_liq_total, 1e-12)
        pm_in = max(pm_inlet, 1e-12)
        
        co2_pct = max(0.0, min(100.0, (co2_in - max(y_uniform[0, -1], 0.0)) / co2_in * 100.0))
        so2_pct = max(0.0, min(100.0, (so2_in - max(y_uniform[5, -1], 0.0)) / so2_in * 100.0))
        nox_pct = max(0.0, min(100.0, (nox_in - max(y_uniform[11, -1], 0.0)) / nox_in * 100.0))
        pm_pct = max(0.0, min(100.0, max(y_uniform[16, -1], 0.0) / pm_in * 100.0))
        metal_pct = max(0.0, min(100.0, max(y_uniform[15, -1], 0.0) / metal_in * 100.0))
        
        diagnostics = {
            "solver_method": self.config.method,
            "nfev": int(sol.nfev),
            "njev": int(sol.njev),
            "nlu": int(sol.nlu),
        }
        
        input_str = f"{plant.id}:{reagent.id}:{conditions}"
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        computation_time = time.perf_counter() - start_time
        
        return KineticsResult(
            final_state={
                "co2_aq": float(y_uniform[0, -1]),
                "hco3": float(y_uniform[1, -1]),
                "ca_free": float(y_uniform[3, -1]),
                "caco3_s": float(y_uniform[4, -1]),
                "so2_aq": float(y_uniform[5, -1]),
                "caso4_s": float(y_uniform[10, -1]),
                "ca_active": float(y_uniform[14, -1]),
                "metal_chelated": float(y_uniform[15, -1]),
                "pm_trapped": float(y_uniform[16, -1]),
            },
            time_series={
                "t": t_uniform,
                "co2_aq": y_uniform[0],
                "hco3": y_uniform[1],
                "ca_free": y_uniform[3],
                "caco3_s": y_uniform[4],
                "so2_aq": y_uniform[5],
                "caso4_s": y_uniform[10],
                "ca_active": y_uniform[14],
                "pm_trapped": y_uniform[16],
            },
            capture_efficiencies={
                "co2_pct": float(co2_pct),
                "so2_pct": float(so2_pct),
                "pm_pct": float(pm_pct),
                "metal_pct": float(metal_pct),
                "nox_pct": float(nox_pct),
            },
            diagnostics=diagnostics,
            input_hash=input_hash,
            computation_time_s=computation_time,
        )

    def _compute_initial_conditions(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions,
    ) -> np.ndarray:
        # Henry's law for CO2
        T_K = float(conditions.reactor_temp_c) + 273.15
        H_co2 = HENRY_CO2
        p_co2 = float(plant.co2_vol_pct) / 100.0 * 101325.0
        co2_aq_0 = H_co2 * p_co2
        
        # Henry's law for SO2
        H_so2 = HENRY_SO2
        p_so2 = float(plant.so2_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["SO2"] * 1e6)
        so2_aq_0 = H_so2 * p_so2
        
        # Henry's law for NO2
        H_no2 = HENRY_NO2
        p_no2 = float(plant.nox_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["NO2"] * 1e6)
        nox_aq_0 = H_no2 * p_no2
        
        # Calcium concentration from reagent
        ca_wt = float(reagent.ca_wt_pct) / 100.0
        ca_density = 1010.0
        ca_free_0 = ca_wt * ca_density * 1000.0 / MOLAR_MASSES["CaOH2"]
        
        y0 = np.zeros(17)
        y0[0] = co2_aq_0
        y0[1] = 1.0
        y0[3] = ca_free_0
        y0[5] = so2_aq_0
        y0[11] = nox_aq_0
        y0[13] = 10**-8.5  # pH 8.5
        y0[14] = float(reagent.enzyme_mg_per_l)
        
        return y0
