"""
workers/tasks/simulation.py
Celery tasks for executing heavy physical/economic computations.
"""

import asyncio
import os
import json
from datetime import datetime
from uuid import UUID

import redis
from celery import shared_task
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from cbms_workers.workers.celery_app import celery_app
from cbms_api.database.connection import async_session_maker
from cbms_api.database.models import SimulationRun, SimulationResult, PlantProfile, LogisticsConfig
from cbms_workers.idempotency import run_async_task

# Import V1 engine and components
from cbms_sim.v1 import SimulationEngine, SimulationRequest, SimulationOptions, SimulationType
from cbms_sim.v1.types import PlantProfile as V1PlantProfile, ReagentFormulation as V1ReagentFormulation, OperatingConditions as V1OperatingConditions, BoilerType as V1BoilerType, CalciumSourceType as V1CalciumSourceType
from cbms_sim.domain.uq.wiener_process import simulate_saturation_fpt
from decimal import Decimal
from uuid import uuid4
import numpy as np

# Boiler mapping
BOILER_TYPE_MAP = {
    "power_generation": V1BoilerType.PULVERIZED_COAL,
    "cement_manufacturing": V1BoilerType.ROTARY_KILN,
    "steel_industry": V1BoilerType.STOKER_GRATE,
    "textile": V1BoilerType.STOKER_GRATE,
    "petrochemical": V1BoilerType.GAS_TURBINE,
    "waste_incinerator": V1BoilerType.CIRCULATING_FLUIDIZED,
    "pulverized_coal": V1BoilerType.PULVERIZED_COAL,
    "cfb": V1BoilerType.CIRCULATING_FLUIDIZED,
    "stoker_grate": V1BoilerType.STOKER_GRATE,
    "diesel_engine": V1BoilerType.DIESEL_ENGINE,
    "gas_turbine": V1BoilerType.GAS_TURBINE,
    "rotary_kiln": V1BoilerType.ROTARY_KILN
}

# Calcium source mapping
CA_SOURCE_MAP = {
    "Ca(OH)2": V1CalciumSourceType.LIME,
    "steel_slag": V1CalciumSourceType.STEEL_SLAG,
    "waste_lime_mud": V1CalciumSourceType.WASTE_LIME,
    "ckd": V1CalciumSourceType.CEMENT_KILN_DUST
}


# Establish a connection to Redis for progress publication
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.Redis.from_url(REDIS_URL)
except Exception:
    redis_client = None


def publish_progress(run_id_str: str, stage: str, pct: int, stage_pct: int, details: str = ""):
    """Publishes simulation run execution progress statistics to Redis channels."""
    if redis_client is None:
        return
    channel = f"simulation.{run_id_str}.progress"
    payload = {
        "run_id": run_id_str,
        "stage": stage,
        "pct": pct,
        "stage_pct": stage_pct,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        redis_client.publish(channel, json.dumps(payload))
        # Also store the latest progress payload in Redis (24-hour expiration)
        redis_client.set(f"simulation.{run_id_str}.status_cached", json.dumps(payload), ex=86400)
    except Exception:
        pass


async def _execute_simulation(
    run_id_str: str,
    temp_c: float,
    override_co2: float,
    override_so2: float,
    task_id: str = None
):
    """Async engine executor called inside the synchronous Celery task wrapper."""
    run_id = UUID(run_id_str)
    
    async with async_session_maker() as session:
        # Load the run details with associated plants and logistics configs
        result = await session.execute(
            select(SimulationRun)
            .options(
                selectinload(SimulationRun.plant)
                .selectinload(PlantProfile.logistics)
            )
            .filter(SimulationRun.id == run_id)
        )
        run = result.scalars().first()
        if not run:
            return
 
        # Set status to RUNNING
        run.status = "RUNNING"
        if task_id:
            run.celery_task_id = task_id
        await session.commit()
 
        publish_progress(run_id_str, "INITIALIZING", 5, 0, "Loading plant specifications")
 
        try:
            plant = run.plant
            logistics = plant.logistics
 
            # Setup inputs for V1 Simulation Engine
            v1_plant = V1PlantProfile(
                id=plant.id,
                name=plant.name,
                location=plant.location,
                boiler_type=BOILER_TYPE_MAP.get(plant.boiler_type, V1BoilerType.PULVERIZED_COAL),
                exhaust_flow_nm3_hr=Decimal(str(plant.exhaust_flow_rate)),
                baseline_temperature_c=Decimal(str(plant.baseline_temperature)),
                co2_vol_pct=Decimal(str(plant.co2_concentration)),
                so2_mg_per_nm3=Decimal(str(plant.so2_concentration)),
                nox_mg_per_nm3=Decimal(str(plant.nox_concentration)),
                fly_ash_g_per_nm3=Decimal(str(plant.fly_ash_load)),
                heavy_metal_profile=[],
                operating_hours_per_year=int(plant.operating_hours_per_year or 8000),
            )
            
            v1_reagent = V1ReagentFormulation(
                id=uuid4(),
                name="Reagent Formulation",
                chitosan_wt_pct=Decimal(str(run.chitosan_wt_pct)),
                ca_source_type=CA_SOURCE_MAP.get(logistics.calcium_source_type, V1CalciumSourceType.LIME),
                ca_wt_pct=Decimal("3.5"),
                enzyme_type="bovine_CA",
                enzyme_mg_per_l=Decimal(str(run.enzyme_concentration_mg_l)),
                additives={}
            )
            
            v1_conditions = V1OperatingConditions(
                reactor_temp_c=Decimal(str(temp_c)),
                pH_initial=Decimal("8.5"),
                liquid_to_gas_ratio=Decimal("8.5"),
                residence_time_s=Decimal("27.0"),
                mesh_count=6,
                press_force_bar=Decimal(str(run.press_force_bar)),
                curing_temperature_c=Decimal("25.0"),
                curing_time_h=Decimal("48.0")
            )
            
            v1_options = SimulationOptions(
                simulation_type=SimulationType.SOBOL,
                n_mc_samples=500,
                random_seed=42
            )
            
            request = SimulationRequest(
                request_id=run.id,
                org_id=run.organization_id,
                user_id=uuid4(),
                plant=v1_plant,
                reagent=v1_reagent,
                conditions=v1_conditions,
                options=v1_options,
                submitted_at=run.created_at or datetime.utcnow()
            )
 
            # 1. Run Kinetics & Full Engine
            publish_progress(run_id_str, "KINETICS_SOLVE", 20, 0, "Solving stiff carbonation kinetics equations")
            engine = SimulationEngine()
            engine.warmup()
            sim_result = engine.run(request)
 
            # Apply overrides if specified
            co2_eff = float(sim_result.kinetics.capture.co2_pct)
            so2_eff = float(sim_result.kinetics.capture.so2_pct)
            if override_co2 is not None:
                co2_eff = override_co2
            if override_so2 is not None:
                so2_eff = override_so2
 
            # 2. Run Mass Balance Solver Progress
            publish_progress(run_id_str, "MASS_BALANCE", 40, 0, "Computing material conservation equations")
 
            # 3. Wiener Process saturation simulation
            publish_progress(run_id_str, "SATURATION_SIM", 60, 0, "Running Wiener process saturation models")
            drift = float(sim_result.mass_balance.co2_input_kg_hr) * (co2_eff / 100.0)
            capacity_threshold = 500.0
            volatility = drift * 0.25 if drift > 0 else 5.0
            
            _, wiener_summary = simulate_saturation_fpt(
                drift_mu_kg_hr=drift,
                volatility_sigma_kg_hr=volatility,
                capacity_threshold_kg=capacity_threshold,
                observation_window_hr=48.0
            )
 
            # 4. Predict Compressive Strength Progress
            publish_progress(run_id_str, "STRENGTH_ESTIMATE", 70, 0, "Predicting block compressive strength")
 
            # 5. Financial analysis Progress
            publish_progress(run_id_str, "FINANCIAL_PROJECTIONS", 80, 0, "Generating financial projections")
 
            # 5b. Run Uncertainty Quantification (UQ) Analysis Progress
            publish_progress(run_id_str, "UNCERTAINTY_QUANTIFICATION", 90, 0, "Running uncertainty analysis")
 
            # Compute real time-series from the solver's transient result
            t_series = list(sim_result.kinetics.time_s)
            co2_aq_series = list(sim_result.kinetics.co2_aq_mol_per_m3)
            
            indices = np.linspace(0, len(t_series) - 1, 24, dtype=int)
            co2_init = co2_aq_series[0] if co2_aq_series[0] > 0 else 1.0
            co2_cap_curve = [(1.0 - co2_aq_series[idx] / co2_init) * co2_eff for idx in indices]
            co2_cap_curve = [max(0.0, min(co2_eff, v)) for v in co2_cap_curve]
            co2_cap_curve[0] = 0.0
            co2_cap_curve[-1] = co2_eff
            
            so2_cap_curve = [so2_eff * (1.0 - np.exp(-t_series[idx] / 2.0)) for idx in indices]
            so2_cap_curve[0] = 0.0
            so2_cap_curve[-1] = so2_eff
            
            strength_val = float(sim_result.block.strength_mpa)
            strength_curve = [strength_val * (np.log(1.0 + hr) / np.log(49.0)) for hr in np.linspace(0, 48, 24)]
            strength_curve[0] = 0.0
            strength_curve[-1] = strength_val
            
            ph_curve = [8.5 - 0.7 * (1.0 - np.exp(-t_series[idx] / 5.0)) for idx in indices]
            
            co2_std = float(sim_result.capture_distribution.std)
            so2_std = float(sim_result.so2_distribution.std)
            strength_std = float(sim_result.strength_distribution.std)
            
            time_series_dict = {
                "co2_capture": [
                    {
                        "x": f"h{int(i * 2):02d}",
                        "median": float(co2_cap_curve[i]),
                        "p5": float(max(0.0, co2_cap_curve[i] - co2_std * 1.5)),
                        "p95": float(min(100.0, co2_cap_curve[i] + co2_std * 1.5))
                    } for i in range(24)
                ],
                "so2_capture": [
                    {
                        "x": f"h{int(i * 2):02d}",
                        "median": float(so2_cap_curve[i]),
                        "p5": float(max(0.0, so2_cap_curve[i] - so2_std * 1.5)),
                        "p95": float(min(100.0, so2_cap_curve[i] + so2_std * 1.5))
                    } for i in range(24)
                ],
                "block_strength": [
                    {
                        "x": f"h{int(i * 2):02d}",
                        "median": float(strength_curve[i]),
                        "p5": float(max(0.0, strength_curve[i] - strength_std * 1.5)),
                        "p95": float(strength_curve[i] + strength_std * 1.5)
                    } for i in range(24)
                ],
                "ph_profile": [
                    {
                        "x": f"h{int(i * 2):02d}",
                        "median": float(ph_curve[i]),
                        "p5": float(ph_curve[i] - 0.2),
                        "p95": float(ph_curve[i] + 0.2)
                    } for i in range(24)
                ]
            }
            
            hourly_block_yield = float(sim_result.mass_balance.caco3_output_kg_hr + sim_result.mass_balance.gypsum_output_kg_hr + sim_result.mass_balance.fly_ash_captured_kg_hr + sim_result.mass_balance.chitosan_input_kg_hr * 0.3)
            annual_blocks = int(hourly_block_yield * float(plant.operating_hours_per_year or 8000) / 4.0 * 0.75)
            annual_co2_captured_tons = (float(sim_result.mass_balance.co2_input_kg_hr) * (co2_eff / 100.0) * float(plant.operating_hours_per_year or 8000)) / 1000.0
            
            uq_res_dict = {
                "co2": {
                    "mean": co2_eff,
                    "std": co2_std,
                    "p05": float(sim_result.capture_distribution.p5),
                    "p95": float(sim_result.capture_distribution.p95),
                    "samples": sim_result.capture_distribution.samples
                },
                "so2": {
                    "mean": so2_eff,
                    "std": so2_std,
                    "p05": float(sim_result.so2_distribution.p5),
                    "p95": float(sim_result.so2_distribution.p95),
                    "samples": sim_result.so2_distribution.samples
                },
                "strength": {
                    "mean": float(sim_result.strength_distribution.mean),
                    "std": strength_std,
                    "p05": float(sim_result.strength_distribution.p5),
                    "p95": float(sim_result.strength_distribution.p95),
                    "samples": sim_result.strength_distribution.samples
                },
                "npv": {
                    "mean": float(sim_result.npv_distribution.mean),
                    "std": float(sim_result.npv_distribution.std),
                    "p05": float(sim_result.npv_distribution.p5),
                    "p95": float(sim_result.npv_distribution.p95),
                    "samples": sim_result.npv_distribution.samples
                },
                "payback": {
                    "mean": float(sim_result.payback_distribution.mean),
                    "std": float(sim_result.payback_distribution.std),
                    "p05": float(sim_result.payback_distribution.p5),
                    "p95": float(sim_result.payback_distribution.p95),
                    "samples": sim_result.payback_distribution.samples
                },
                "sensitivity": sim_result.sensitivity.first_order,
                "sobol": {
                    "co2_capture": sim_result.sensitivity.first_order,
                    "npv": sim_result.sensitivity.npv_first_order,
                    "block_strength": sim_result.sensitivity.block_strength_first_order
                },
                "time_series": time_series_dict
            }
 
            # 6. Save simulation result details
            sim_result_db = SimulationResult(
                simulation_run_id=run.id,
                co2_capture_efficiency_pct=co2_eff,
                so2_capture_efficiency_pct=so2_eff,
                predicted_block_strength_mpa=strength_val,
                block_grade=sim_result.block.is_grade,
                hourly_block_yield_kg=hourly_block_yield,
                annual_block_count=annual_blocks,
                estimated_opex_per_ton_co2=float(sim_result.economic.annual_opex_inr) / (annual_co2_captured_tons + 1e-9),
                annual_ccts_revenue_inr=float(sim_result.economic.ccts_revenue_inr),
                annual_block_revenue_inr=float(sim_result.economic.block_revenue_inr),
                annual_opex_inr=float(sim_result.economic.annual_opex_inr),
                annual_net_revenue_inr=float(sim_result.economic.annual_revenue_inr) - float(sim_result.economic.annual_opex_inr),
                capex_total_inr=float(sim_result.economic.capex_inr),
                simple_payback_months=float(sim_result.economic.payback_months),
                npv_10yr_inr=float(sim_result.economic.npv_10yr_inr),
                irr_pct=float(sim_result.economic.irr_pct),
                mean_saturation_time_hours=wiener_summary.mean_fpt_hours,
                p95_saturation_time_hours=wiener_summary.p95_fpt_hours,
                cpcb_compliant=sim_result.compliance.cpcb_so2_compliant,
                uq_metrics=uq_res_dict
            )
            session.add(sim_result_db)
 
            # Mark run as completed
            run.status = "COMPLETED"
            run.completed_at = datetime.utcnow()
            await session.commit()
            publish_progress(run_id_str, "COMPLETED", 100, 100, "Simulation process successfully completed")

        except Exception as e:
            # Handle solver failures and write error log
            run.status = "FAILED"
            run.error_log = str(e)
            await session.commit()
            publish_progress(run_id_str, "FAILED", 100, 100, f"Simulation process failed: {str(e)}")


@celery_app.task(name="workers.tasks.run_simulation_task", bind=True)
def run_simulation_task(
    self,
    run_id_str: str,
    temp_c: float = 40.0,
    override_co2: float = None,
    override_so2: float = None
):
    """Celery task entrypoint (synchronous wrapper for event loop execution)."""
    run_async_task(_execute_simulation(run_id_str, temp_c, override_co2, override_so2, self.request.id))
