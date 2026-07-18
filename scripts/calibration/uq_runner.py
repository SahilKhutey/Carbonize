"""
Re-run UQ analysis using calibrated parameter distributions.
"""

from __future__ import annotations

from cbms_sim.v1 import SimulationEngine, SimulationRequest, SimulationOptions, SimulationType
from cbms_sim.v1.types import PlantProfile, ReagentFormulation, OperatingConditions, BoilerType, CalciumSourceType
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class UQRunner:
    """Re-run UQ analysis using calibrated parameters."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
    def run(
        self,
        parameters: dict,
        n_samples: int = 30,
    ) -> dict:
        self.logger.info("running_uq_re_analysis", n_samples=n_samples)
        
        engine = SimulationEngine()
        
        request = SimulationRequest(
            request_id=uuid4(),
            org_id=uuid4(),
            user_id=uuid4(),
            plant=PlantProfile(
                id=uuid4(),
                name="Calibrated Plant",
                location="A-City",
                boiler_type=BoilerType.PULVERIZED_COAL,
                exhaust_flow_nm3_hr=Decimal("10000.0"),
                baseline_temperature_c=Decimal("150.0"),
                co2_vol_pct=Decimal("14.0"),
                so2_mg_per_nm3=Decimal("1200.0"),
                nox_mg_per_nm3=Decimal("500.0"),
                fly_ash_g_per_nm3=Decimal("4.5"),
                operating_hours_per_year=8000,
            ),
            reagent=ReagentFormulation(
                id=uuid4(),
                name="Calibrated Reagent",
                chitosan_wt_pct=Decimal("3.0"),
                ca_source_type=CalciumSourceType.LIME,
                ca_wt_pct=Decimal("3.5"),
                enzyme_mg_per_l=Decimal("12.0"),
            ),
            conditions=OperatingConditions(
                reactor_temp_c=Decimal("40.0"),
                pH_initial=Decimal("8.5"),
                liquid_to_gas_ratio=Decimal("8.5"),
                residence_time_s=Decimal("27.0"),
                press_force_bar=Decimal("200.0"),
            ),
            options=SimulationOptions(
                simulation_type=SimulationType.MONTE_CARLO,
                n_mc_samples=n_samples,
                random_seed=42
            ),
            submitted_at=datetime.now(timezone.utc)
        )
        
        res = engine.run(request)
        
        return {
            "co2_capture_pct": {
                "mean": res.capture_distribution.mean,
                "std": res.capture_distribution.std,
                "p5": res.capture_distribution.p5,
                "p95": res.capture_distribution.p95
            },
            "so2_capture_pct": {
                "mean": res.so2_distribution.mean,
                "std": res.so2_distribution.std
            }
        }
