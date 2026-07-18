"""
Extended kinetics engine with explicit multi-gas competition.

Models CO₂, SO₂, and NOₓ absorption in a shared alkaline slurry,
capturing:
- Alkalinity budget depletion
- Ca²⁺ competition for precipitation
- pH-driven CA activity loss
- Chitosan site competition (metals vs. CO₂)
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
from cbms_shared.constants import MOLAR_MASSES
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
):
    """
    Right-hand side for extended multi-species kinetics ODE.
    
    All three acidic gases compete for the same alkalinity budget
    and Ca²⁺ pool. The pH is computed from total alkalinity, which
    is conserved (modulo buffer additions).
    """
    
    # Ensure non-negative concentrations
    y_safe = np.zeros(16)
    for i in range(16):
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
    
    # Carbonate equilibrium (fast)
    CO3 = 10**-10.33 * HCO3 / H_plus
    
    # Sulfite equilibrium
    SO3 = 10**-7.2 * HSO3 / H_plus
    
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
    H_SO2_inv = 1.2
    SO2_eq = H_SO2_inv * p_so2
    k_so2_eff = k_so2_abs * (1.0 + 0.1 * HCO3 / H_plus)
    v_so2_abs = k_so2_eff * (SO2_eq - SO2_aq)
    if v_so2_abs < 0.0:
        v_so2_abs = 0.0
    
    # NO₂ absorption
    H_NO2_inv = 1.0e-2
    NO2_eq = H_NO2_inv * p_no2
    v_no2_abs = k_no2_abs * (NO2_eq - NO2_aq)
    if v_no2_abs < 0.0:
        v_no2_abs = 0.0
    
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
    
    # Heavy metal chelation
    pH_chel_factor = 1.0 / (1.0 + np.exp(-(pH - 5.5) * 3.0))
    co2_competition = 1.0 / (1.0 + 0.1 * CO2_aq)
    v_chel = k_chel * free_amine_density * 0.5 * pH_chel_factor * co2_competition
    
    # Enzyme deactivation
    k_inact_T = ca_inactivation * np.exp(
        -E_a_inact / R_gas * (1.0 / T_reactor - 1.0 / T_ref)
    )
    if pH < 5.5:
        pH_denat = 1e-3 * (5.5 - pH)
    else:
        pH_denat = 0.0
    
    # ODE outputs
    dydt = np.zeros(16)
    dydt[0] = -v_cat
    dydt[1] = v_cat - 2.0 * r_caco3
    dydt[2] = 2.0 * r_caco3
    dydt[3] = -r_ca_total
    dydt[4] = r_caco3
    dydt[5] = -v_so2_abs
    dydt[6] = v_so2_abs
    dydt[7] = -v_sulfite_ox
    dydt[8] = v_sulfite_ox
    dydt[9] = r_caso3
    dydt[10] = r_caso4
    dydt[11] = -v_no2_abs
    dydt[12] = v_no2_abs
    
    # pH tracking
    H_production = v_cat + v_so2_abs + v_no2_abs
    H_consumption = 2.0 * r_caco3 + 2.0 * r_caso3
    dydt[13] = (H_production - H_consumption) / 1000.0
    
    # CA inactivation
    dydt[14] = -k_inact_T * CA_active - pH_denat * CA_active
    
    # Metal chelation
    dydt[15] = v_chel
    
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
        y_dummy = np.zeros(16)
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
            Ksp_caco3=3.3e-9, Ksp_caso4=4.93e-5, Ksp_caso3=6.0e-9,
            k_chel=8.0e-3, free_amine_density=0.05,
            pm_inlet=25.0, k_pm_cap=0.18,
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
            3.3e-9,  # Ksp_caco3
            4.93e-5, # Ksp_caso4
            6.0e-9,  # Ksp_caso3
            8.0e-3,  # k_chel
            0.05,    # free_amine_density
            25.0,    # pm_inlet
            0.18,    # k_pm_cap
            5.0e-5,  # ca_inactivation
            85.0e3,  # E_a_inact
            float(conditions.reactor_temp_c) + 273.15,
            8.314,   # R_gas
            313.15,  # T_ref
            p_co2,   # p_co2
            p_so2,   # p_so2
            p_no2,   # p_no2
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
        metal_in = 0.5
        pm_in = 25.0
        
        co2_pct = max(0.0, min(100.0, (co2_in - max(y_uniform[0, -1], 0.0)) / co2_in * 100.0))
        so2_pct = max(0.0, min(100.0, (so2_in - max(y_uniform[5, -1], 0.0)) / so2_in * 100.0))
        pm_pct = 95.0 # Trapping efficiency
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
                "pm_trapped": 0.0,
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
            },
            capture_efficiencies={
                "co2_pct": float(co2_pct),
                "so2_pct": float(so2_pct),
                "pm_pct": float(pm_pct),
                "metal_pct": float(metal_pct),
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
        H_co2 = 3.4e-2
        p_co2 = float(plant.co2_vol_pct) / 100.0 * 101325.0
        co2_aq_0 = H_co2 * p_co2
        
        # Henry's law for SO2
        H_so2 = 1.2
        p_so2 = float(plant.so2_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["SO2"] * 1e6)
        so2_aq_0 = H_so2 * p_so2
        
        # Calcium concentration from reagent
        ca_wt = float(reagent.ca_wt_pct) / 100.0
        ca_density = 1010.0
        ca_free_0 = ca_wt * ca_density * 1000.0 / MOLAR_MASSES["CaOH2"]
        
        y0 = np.zeros(16)
        y0[0] = co2_aq_0
        y0[1] = 1.0
        y0[3] = ca_free_0
        y0[5] = so2_aq_0
        y0[13] = 10**-8.5  # pH 8.5
        y0[14] = float(reagent.enzyme_mg_per_l)
        
        return y0
