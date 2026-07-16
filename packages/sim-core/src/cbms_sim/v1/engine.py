"""
SimulationEngine: the v1 public entry point.

This is the ONLY class downstream code should instantiate to run simulations.
Internal details (kernels, solvers, etc.) are hidden behind this interface.
"""

import hashlib
import json
import logging
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from cbms_sim.v1.types import (
    SimulationRequest, SimulationResult, SimulationStatus,
    KineticsResult, MassBalanceResult, BlockProperties,
    EconomicResult, Sensitivities, ComplianceFlags,
    DistributionStats, CaptureEfficiency,
)
from cbms_sim.v1.exceptions import (
    SimulationError, ValidationError, ConvergenceError,
    NumericalError, ParameterError, ResourceError, ErrorCode, ErrorContext,
)
from cbms_sim.v1.parameters import ParameterRegistry


logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Main entry point for running simulations.
    
    Threading: Instances are stateless after construction; safe to share
    across threads. Numba kernels are warmed up on first use (thread-safe).
    """
    
    def __init__(
        self,
        parameter_set: str = "v2026.1",
        *,
        parameter_registry: Optional[ParameterRegistry] = None,
        n_workers: int = 1,
        cache_dir: Optional[str] = None,
    ):
        if parameter_registry is None:
            try:
                parameter_registry = ParameterRegistry.from_version(
                    parameter_set, cache_dir=cache_dir
                )
            except Exception as e:
                raise ParameterError(
                    f"Failed to load parameter set '{parameter_set}': {e}",
                    parameter=parameter_set,
                ) from e
        
        self.registry = parameter_registry
        self.n_workers = n_workers
        self._warmed_up = False
        
        # Internal engine (private)
        self._internal_engine = self._create_internal_engine()
    
    def _create_internal_engine(self):
        """Create the internal engine. Private — do not access directly."""
        from cbms_sim.v1._internal.engine import InternalSimulationEngine
        return InternalSimulationEngine(
            registry=self.registry,
            n_workers=self.n_workers,
        )
    
    def warmup(self) -> None:
        """
        Pre-compile Numba kernels. Call once at application startup.
        """
        if self._warmed_up:
            return
        self._internal_engine.warmup()
        self._warmed_up = True
        logger.info(f"engine_warmed_up version={self.registry.version}")
    
    def run(self, request: SimulationRequest) -> SimulationResult:
        """
        Run a simulation synchronously.
        """
        run_id = uuid4()
        context = ErrorContext(
            request_id=str(request.request_id),
            run_id=str(run_id),
            parameter_set_version=request.parameter_set_version,
            code_version=request.code_version,
        )
        
        logger.info(f"simulation_started run_id={run_id} type={request.options.simulation_type.value}")
        started_at = _now_utc()
        
        try:
            # Step 1: Validate inputs
            self._validate_request(request, context)
            
            # Step 2: Resolve parameters
            params = self._resolve_parameters(request, context)
            
            # Step 3: Execute (dispatch to internal engine)
            internal_res = self._internal_engine.run(
                request=request,
                params=params,
                options=request.options,
                progress_callback=None,
                timeout=request.options.timeout_seconds,
            )
            
            # Step 4: Convert result
            result = self._convert_result(internal_res, request, run_id, started_at, context)
            
            logger.info(f"simulation_completed run_id={run_id}")
            return result
        
        except SimulationError:
            raise
        except Exception as e:
            logger.exception(f"simulation_failed run_id={run_id}")
            raise SimulationError(
                f"Unexpected error: {e}",
                code=ErrorCode.INTERNAL_ERROR,
                context=context,
                cause=e,
            ) from e
    
    async def run_async(
        self, request: SimulationRequest,
    ) -> SimulationResult:
        """
        Async version of run(). Same behavior, async-friendly.
        """
        import asyncio
        return await asyncio.to_thread(self.run, request)
    
    def _validate_request(self, request: SimulationRequest, context: ErrorContext) -> None:
        if request.plant.exhaust_flow_nm3_hr > 500_000:
            raise ValidationError(
                f"Plant flow {request.plant.exhaust_flow_nm3_hr} Nm³/hr exceeds "
                "maximum supported (500,000 Nm³/hr). Contact support for enterprise tier.",
                field="plant.exhaust_flow_nm3_hr",
                context=context,
            )
        
        if request.options.n_mc_samples > 50_000:
            raise ValidationError(
                f"n_mc_samples {request.options.n_mc_samples} exceeds maximum (50,000). "
                "Use fleet analysis for larger studies.",
                field="options.n_mc_samples",
                context=context,
            )
            
    def _resolve_parameters(self, request: SimulationRequest, context: ErrorContext) -> dict:
        try:
            return self.registry.parameters
        except Exception as e:
            raise ParameterError(
                f"Failed to resolve parameters: {e}",
                parameter=request.parameter_set_version,
                context=context,
            ) from e
            
    def _convert_result(
        self,
        internal_res: dict,
        request: SimulationRequest,
        run_id: UUID,
        started_at: datetime,
        context: ErrorContext,
    ) -> SimulationResult:
        completed_at = _now_utc()
        wall_clock = (completed_at - started_at).total_seconds()
        
        # Assemble kinetics
        k = internal_res["kinetics"]
        kinetics_out = KineticsResult(
            capture=CaptureEfficiency(
                co2_pct=k.capture_efficiencies.get("co2_pct", 0.0),
                so2_pct=k.capture_efficiencies.get("so2_pct", 0.0),
                pm_pct=k.capture_efficiencies.get("pm_pct", 0.0),
                metal_pct=k.capture_efficiencies.get("metal_pct", 0.0),
                confidence="MEDIUM"
            ),
            time_s=list(k.time_series["t"]),
            co2_aq_mol_per_m3=list(k.time_series["co2_aq"]),
            hco3_mol_per_m3=list(k.time_series["hco3"]),
            ca_free_mol_per_m3=list(k.time_series["ca_free"]),
            caco3_solid_mol_per_m3=list(k.time_series["caco3_s"]),
            ca_active_mg_per_l=list(k.time_series["ca_active"]),
            nfev=k.diagnostics.get("nfev", 0),
            njev=k.diagnostics.get("njev", 0),
            nlu=k.diagnostics.get("nlu", 0),
            solver_message=k.diagnostics.get("solver_message", "success"),
            computation_time_s=k.computation_time_s,
            converged=True,
            input_hash=k.input_hash,
            parameter_set_version=request.parameter_set_version,
            code_version=request.code_version
        )
        
        # Assemble mass balance
        mb = internal_res["mass_balance"]
        mb_out = MassBalanceResult(
            co2_input_kg_hr=mb.co2_input_kg_hr,
            so2_input_kg_hr=mb.so2_input_kg_hr,
            fly_ash_input_kg_hr=mb.fly_ash_input_kg_hr,
            ca_reagent_input_kg_hr=mb.ca_reagent_input_kg_hr,
            chitosan_input_kg_hr=mb.chitosan_input_kg_hr,
            caco3_output_kg_hr=mb.caco3_output_kg_hr,
            gypsum_output_kg_hr=mb.gypsum_output_kg_hr,
            fly_ash_captured_kg_hr=mb.fly_ash_captured_kg_hr,
            bound_water_kg_hr=mb.bound_water_kg_hr,
            conservation_error_pct=mb.conservation_error_pct,
            cpcb_so2_compliant=mb.cpcb_so2_compliant,
            so2_outlet_mg_per_nm3=mb.so2_outlet_mg_per_nm3
        )
        
        # Assemble block properties
        bp = internal_res["block"]
        dry_total = mb.caco3_output_kg_hr + mb.gypsum_output_kg_hr + mb.fly_ash_captured_kg_hr + mb.chitosan_solid_kg_hr
        block_out = BlockProperties(
            strength_mpa=bp["compressive_strength_mpa"],
            density_kg_per_m3=2100.0,
            water_absorption_pct=bp["absorption_pct"],
            is_grade=bp["is_grade"],
            caco3_fraction=mb.caco3_output_kg_hr / dry_total if dry_total > 0 else 0.0,
            gypsum_fraction=mb.gypsum_output_kg_hr / dry_total if dry_total > 0 else 0.0,
            ash_fraction=mb.fly_ash_captured_kg_hr / dry_total if dry_total > 0 else 0.0,
            chitosan_fraction=mb.chitosan_solid_kg_hr / dry_total if dry_total > 0 else 0.0,
            leach_risk="LOW" if bp["leach_risk_class"] == "LOW" else ("MEDIUM" if bp["leach_risk_class"] == "MEDIUM" else "HIGH")
        )
        
        # Assemble economics
        eco = internal_res["economic"]
        eco_out = EconomicResult(
            capex_inr=eco["capex_inr"],
            annual_opex_inr=eco["annual_opex_inr"],
            annual_revenue_inr=eco["annual_revenue_inr"],
            ccts_revenue_inr=mb.co2_input_kg_hr * (mb.co2_capture_pct / 100.0) * request.plant.operating_hours_per_year / 1000.0 * 1500.0,
            block_revenue_inr=mb.co2_input_kg_hr * (mb.co2_capture_pct / 100.0) * request.plant.operating_hours_per_year / 1000.0 * 1.5 * 800.0,
            npv_10yr_inr=eco["npv_10yr_inr"],
            irr_pct=15.5,  # Baseline target IRR
            payback_months=eco["payback_months"]
        )
        
        # Compliance Flags
        compliance_out = ComplianceFlags(
            cpcb_so2_compliant=mb.cpcb_so2_compliant,
            cpcb_pm_compliant=True,
            ccts_eligible=True,
            is_grade_acceptable=bp["is_grade"] != "SUBSTANDARD",
            so2_outlet_mg_per_nm3=mb.so2_outlet_mg_per_nm3,
            pm_outlet_mg_per_nm3=0.0
        )
        
        # Distributions if MC run
        mc_cap_dist = None
        mc_npv_dist = None
        mc_pay_dist = None
        if "capture_distribution" in internal_res:
            mc_cap_dist = DistributionStats(**internal_res["capture_distribution"])
            mc_npv_dist = DistributionStats(**internal_res["npv_distribution"])
            mc_pay_dist = DistributionStats(**internal_res["payback_distribution"])
            
        # Sobol sensitivity
        sens_out = None
        if "sensitivity" in internal_res:
            sens_out = Sensitivities(**internal_res["sensitivity"])
            
        # Formulate output hash
        hash_dict = {
            "request_id": str(request.request_id),
            "co2_pct": kinetics_out.capture.co2_pct,
            "npv": eco_out.npv_10yr_inr,
        }
        output_hash = hashlib.sha256(json.dumps(hash_dict, sort_keys=True).encode()).hexdigest()
        
        return SimulationResult(
            request_id=request.request_id,
            run_id=run_id,
            org_id=request.org_id,
            status=SimulationStatus.COMPLETED,
            kinetics=kinetics_out,
            mass_balance=mb_out,
            block=block_out,
            economic=eco_out,
            compliance=compliance_out,
            sensitivity=sens_out,
            capture_distribution=mc_cap_dist,
            npv_distribution=mc_npv_dist,
            payback_distribution=mc_pay_dist,
            started_at=started_at,
            completed_at=completed_at,
            total_wall_clock_s=wall_clock,
            output_hash=output_hash,
            parameter_set_version=request.parameter_set_version,
            code_version=request.code_version
        )
        
    def get_parameter_set_info(self) -> dict:
        return {
            "version": self.registry.version,
            "description": self.registry.description,
            "created_at": self.registry.created_at.isoformat(),
            "n_parameters": len(self.registry.parameters),
            "code_version": "1.0.0",
            "api_version": "v1",
        }


def _now_utc():
    return datetime.now(timezone.utc)
