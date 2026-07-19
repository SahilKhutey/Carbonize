"""Kinetics engine - the computational heart of the simulation."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp

from cbms_sim.domain.kinetics.kernels import (
    reaction_rhs_numba,
    compute_capture_efficiencies,
)
from cbms_sim.domain.models.plant import PlantProfile
from cbms_sim.domain.models.reagent import ReagentFormulation
from cbms_sim.domain.models.conditions import OperatingConditions
from cbms_sim.domain.models.results import KineticsResult
from cbms_shared.constants import MOLAR_MASSES, MOLAR_VOLUME_STP, HENRY_CO2, HENRY_SO2
from cbms_shared.exceptions import NumericalDivergenceError
from cbms_shared.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class KineticsConfig:
    """Kinetics solver configuration."""
    method: str = "BDF"
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step_s: float = 0.1


class KineticsEngine:
    """
    Solves the 9-species reaction kinetics ODE system.
    
    Uses scipy.integrate.solve_ivp with BDF method for stiff systems.
    Inner loop is Numba-JIT compiled for ~50x speedup.
    """
    
    def __init__(self, config: KineticsConfig | None = None) -> None:
        self.config = config or KineticsConfig()
        self._warmed_up = False
    
    def warmup(self) -> None:
        """Pre-compile Numba kernels."""
        if self._warmed_up:
            return
        
        logger.info("kinetics_warmup_started")
        # Dummy call to trigger JIT compilation
        y_dummy = np.array([1.0, 0.0, 100.0, 0.0, 0.5, 0.0, 12.0, 0.0, 0.0])
        _ = reaction_rhs_numba(
            0.0, y_dummy,
            k_cat=1.0e6, K_M_co2=8.5e-3, k_inact=5.0e-5, E_a_inact=85.0e3,
            k_so2=2.5e-2, k_chel=8.0e-3, ca_cl2=100.0, pH_initial=8.5, T_reactor=313.15,
            p_so2=50.0
        )
        self._warmed_up = True
        logger.info("kinetics_warmup_completed")
    
    def solve(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions,
        residence_time_s: float = 27.0,
    ) -> KineticsResult:
        """
        Solve the kinetics ODE for given inputs.
        
        Args:
            plant: Industrial plant profile
            reagent: Reagent formulation
            conditions: Operating conditions
            residence_time_s: Integration time window
            
        Returns:
            KineticsResult with final state, time series, and diagnostics
            
        Raises:
            NumericalDivergenceError: If solver fails to converge
        """
        if not self._warmed_up:
            self.warmup()
        
        start_time = time.perf_counter()
        
        # Compute initial conditions from gas/liquid equilibrium
        y0 = self._compute_initial_conditions(plant, reagent, conditions)
        
        # Compute p_so2
        p_so2 = float(plant.so2_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["SO2"] * 1e6)

        # Extract inputs for PM and heavy metals
        pm_inlet = float(plant.fly_ash_g_per_nm3)
        metal_inlet = sum(float(m.get("conc_ug_per_nm3", 0.0)) for m in plant.heavy_metal_profile) / 1000.0  # ug/Nm3 to mg/Nm3
        # If metal_inlet is 0 (profile is empty), default to 0.5 for backward compatibility
        if metal_inlet <= 0.0:
            metal_inlet = 0.5
        # If pm_inlet is 0, default to 25.0 for backward compatibility
        if pm_inlet <= 0.0:
            pm_inlet = 25.0
            
        mesh_count = float(conditions.mesh_count)

        # Configure solver
        solver_params = (
            1.0e6,  # k_cat
            8.5e-3,  # K_M_co2
            5.0e-5,  # k_inact
            85.0e3,  # E_a_inact
            2.5e-2,  # k_so2
            8.0e-3,  # k_chel
            float(y0[2]),  # ca_cl2
            float(conditions.pH_initial),
            float(conditions.reactor_temp_c) + 273.15,  # T_reactor in K
            p_so2,  # p_so2 in Pa
            pm_inlet,
            metal_inlet,
            mesh_count,
        )
        
        # Solve ODE
        sol = solve_ivp(
            fun=lambda t, y: reaction_rhs_numba(t, y, *solver_params),
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
                f"Kinetics solver failed: {sol.message}",
                nfev=int(sol.nfev),
                final_time=float(sol.t[-1]),
            )
        
        # Sample at uniform time points
        t_uniform = np.linspace(0, residence_time_s, 1000)
        y_uniform = sol.sol(t_uniform)
        
        # Compute capture efficiencies
        efficiencies = compute_capture_efficiencies(y0, y_uniform[:, -1], pm_inlet=pm_inlet, metal_inlet=metal_inlet)
        
        # Diagnostics
        diagnostics = {
            "solver_method": self.config.method,
            "nfev": int(sol.nfev),
            "njev": int(sol.njev),
            "nlu": int(sol.nlu),
            "final_residual": float(np.max(np.abs(y_uniform[:, -1] - y_uniform[:, -2]) / 0.01)),
            "co2_converged": bool(efficiencies[0] < 95.0),
            "enzyme_deactivation_pct": float(
                (y0[6] - y_uniform[6, -1]) / y0[6] * 100.0
            ),
        }
        
        # Compute input hash for reproducibility
        input_str = f"{plant.id}:{reagent.id}:{conditions}"
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        
        computation_time = time.perf_counter() - start_time
        
        result = KineticsResult(
            final_state={
                "co2_aq": float(y_uniform[0, -1]),
                "hco3": float(y_uniform[1, -1]),
                "ca_free": float(y_uniform[2, -1]),
                "caco3_s": float(y_uniform[3, -1]),
                "so2_aq": float(y_uniform[4, -1]),
                "caso4_s": float(y_uniform[5, -1]),
                "ca_active": float(y_uniform[6, -1]),
                "metal_chelated": float(y_uniform[7, -1]),
                "pm_trapped": float(y_uniform[8, -1]),
            },
            time_series={
                "t": t_uniform,
                "co2_aq": y_uniform[0],
                "hco3": y_uniform[1],
                "ca_free": y_uniform[2],
                "caco3_s": y_uniform[3],
                "so2_aq": y_uniform[4],
                "caso4_s": y_uniform[5],
                "ca_active": y_uniform[6],
            },
            capture_efficiencies={
                "co2_pct": float(efficiencies[0]),
                "so2_pct": float(efficiencies[1]),
                "pm_pct": float(efficiencies[2]),
                "metal_pct": float(efficiencies[3]),
            },
            diagnostics=diagnostics,
            input_hash=input_hash,
            computation_time_s=computation_time,
        )
        
        logger.info(
            "kinetics_solved",
            co2_capture_pct=float(efficiencies[0]),
            so2_capture_pct=float(efficiencies[1]),
            computation_time_s=computation_time,
        )
        
        return result
    
    def _compute_initial_conditions(
        self,
        plant: PlantProfile,
        reagent: ReagentFormulation,
        conditions: OperatingConditions,
    ) -> np.ndarray:
        """Compute initial state vector from gas/liquid equilibrium."""
        # Henry's law for CO2
        T_K = float(conditions.reactor_temp_c) + 273.15
        H_co2 = HENRY_CO2
        p_co2 = float(plant.co2_vol_pct) / 100.0 * 101325.0
        co2_aq_0 = H_co2 * p_co2
        
        # Henry's law for SO2
        H_so2 = HENRY_SO2
        p_so2 = float(plant.so2_mg_per_nm3) * 101325.0 / (MOLAR_MASSES["SO2"] * 1e6)
        so2_aq_0 = H_so2 * p_so2
        
        # Calcium concentration from reagent
        ca_wt = float(reagent.ca_wt_pct) / 100.0
        ca_density = 1010.0  # kg/m³ slurry
        ca_free_0 = ca_wt * ca_density * 1000.0 / MOLAR_MASSES["CaOH2"]
        
        return np.array([
            co2_aq_0,      # [0] CO2_aq
            1.0,           # [1] HCO3- (background)
            ca_free_0,     # [2] Ca2+
            0.0,           # [3] CaCO3_s
            so2_aq_0,      # [4] SO2_aq
            0.0,           # [5] CaSO4_s
            float(reagent.enzyme_mg_per_l),  # [6] CA_active
            0.0,           # [7] Metal_chelated
            0.0,           # [8] PM_trapped
        ])


def solve_kinetics(
    plant: PlantProfile,
    reagent: ReagentFormulation,
    conditions: OperatingConditions,
    residence_time_s: float = 27.0,
) -> KineticsResult:
    """Convenience function for one-shot kinetics solve."""
    from cbms_sim.domain.kinetics.extended_engine import ExtendedKineticsEngine
    engine = ExtendedKineticsEngine()
    return engine.solve(plant, reagent, conditions, residence_time_s)
