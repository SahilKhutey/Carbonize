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

# Import core solver functions
from cbms_sim.core.kinetics import solve_reactor_kinetics
from cbms_sim.core.mass_balance import compute_mass_balance
from cbms_sim.core.wiener_process import simulate_saturation_fpt
from cbms_sim.core.block_strength import predict_compressive_strength, classify_block_grade
from cbms_sim.core.economic_engine import run_financial_analysis
from cbms_sim.core.uncertainty_engine import run_uncertainty_analysis


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

            # 1. Run Kinetics Solver
            publish_progress(run_id_str, "KINETICS_SOLVE", 20, 0, "Solving stiff carbonation kinetics equations")
            kinetics_res = solve_reactor_kinetics(
                co2_vol_pct=float(plant.co2_concentration),
                so2_mg_per_nm3=float(plant.so2_concentration),
                flow_nm3_per_hr=float(plant.exhaust_flow_rate),
                enzyme_mg_per_l=float(run.enzyme_concentration_mg_l),
                calcium_source_g_per_l=35.0,
                reactor_temp_c=temp_c
            )

            # Apply overrides if specified
            if override_co2 is not None:
                kinetics_res["co2_capture_efficiency_pct"] = override_co2
            if override_so2 is not None:
                kinetics_res["so2_capture_efficiency_pct"] = override_so2

            # 2. Run Mass Balance Solver
            publish_progress(run_id_str, "MASS_BALANCE", 40, 0, "Computing material conservation equations")
            mass_res = compute_mass_balance(
                flow_nm3_per_hr=float(plant.exhaust_flow_rate),
                co2_vol_pct=float(plant.co2_concentration),
                so2_mg_per_nm3=float(plant.so2_concentration),
                fly_ash_g_per_nm3=float(plant.fly_ash_load),
                enzyme_mg_per_l=float(run.enzyme_concentration_mg_l),
                chitosan_wt_pct=float(run.chitosan_wt_pct),
                capture_efficiency_overrides={
                    "co": kinetics_res["co2_capture_efficiency_pct"],
                    "so2": kinetics_res["so2_capture_efficiency_pct"]
                }
            )

            # 3. Wiener Process saturation simulation
            publish_progress(run_id_str, "SATURATION_SIM", 60, 0, "Running Wiener process saturation models")
            drift = mass_res.captured_co2_total
            capacity_threshold = 500.0
            volatility = drift * 0.25 if drift > 0 else 5.0
            
            _, wiener_summary = simulate_saturation_fpt(
                drift_mu_kg_hr=drift,
                volatility_sigma_kg_hr=volatility,
                capacity_threshold_kg=capacity_threshold,
                observation_window_hr=48.0
            )

            # 4. Predict Compressive Strength
            publish_progress(run_id_str, "STRENGTH_ESTIMATE", 70, 0, "Predicting block compressive strength")
            strength = predict_compressive_strength(
                mass_balance=mass_res,
                press_force_bar=float(run.press_force_bar),
                curing_hours=48.0,
                temperature_c=25.0
            )
            block_grade = classify_block_grade(strength)

            # 5. Financial analysis
            publish_progress(run_id_str, "FINANCIAL_PROJECTIONS", 80, 0, "Generating financial projections")
            financial = run_financial_analysis(
                mass_balance=mass_res,
                flow_nm3_per_hr=float(plant.exhaust_flow_rate)
            )

            # 5b. Run Uncertainty Quantification (UQ) Analysis
            publish_progress(run_id_str, "UNCERTAINTY_QUANTIFICATION", 90, 0, "Running uncertainty analysis")
            uq_res = run_uncertainty_analysis(
                co2_vol_pct=float(plant.co2_concentration),
                so2_mg_per_nm3=float(plant.so2_concentration),
                flow_nm3_per_hr=float(plant.exhaust_flow_rate),
                enzyme_mg_per_l=float(run.enzyme_concentration_mg_l),
                reactor_temp_c=temp_c,
                sample_count=15
            )

            # 6. Save simulation result details
            sim_result = SimulationResult(
                simulation_run_id=run.id,
                co2_capture_efficiency_pct=kinetics_res["co2_capture_efficiency_pct"],
                so2_capture_efficiency_pct=kinetics_res["so2_capture_efficiency_pct"],
                predicted_block_strength_mpa=strength,
                block_grade=block_grade,
                hourly_block_yield_kg=mass_res.caco3_output + mass_res.gypsum_output + mass_res.fly_ash_captured + mass_res.chitosan_lattice,
                annual_block_count=financial.annual_block_yield_count,
                estimated_opex_per_ton_co2=financial.annual_opex_inr / (financial.annual_co2_captured_tons + 1e-9),
                annual_ccts_revenue_inr=financial.annual_ccts_revenue_inr,
                annual_block_revenue_inr=financial.annual_block_revenue_inr,
                annual_opex_inr=financial.annual_opex_inr,
                annual_net_revenue_inr=financial.annual_net_revenue_inr,
                capex_total_inr=financial.capex_total_inr,
                simple_payback_months=financial.simple_payback_months,
                npv_10yr_inr=financial.npv_10yr_inr,
                irr_pct=financial.irr_pct,
                mean_saturation_time_hours=wiener_summary.mean_fpt_hours,
                p95_saturation_time_hours=wiener_summary.p95_fpt_hours,
                cpcb_compliant=mass_res.cpcb_compliant,
                uq_metrics=uq_res
            )
            session.add(sim_result)

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
