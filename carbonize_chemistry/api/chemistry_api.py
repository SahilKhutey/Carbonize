"""
FastAPI router for Core Chemistry & Hardware Twin API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import time

from ..chemistry.vle import CO2AmineVLE
from ..pollutants.sox import WetLimestoneSOxScrubber, DualAlkaliSOxScrubber
from ..pollutants.nox import SCR_System, SNCR_System
from ..pollutants.mercury import ActivatedCarbonInjection
from ..columns.tray_column import TrayColumnSolver, ColumnSpec, StreamConditions
from ..hardware_twin.plant import CarbonCapturePlant


router = APIRouter(prefix="/v1/chemistry", tags=["chemistry"])


class VLERequest(BaseModel):
    amine: str = 'MEA'
    concentration_wt: float = 30.0
    T: float = 313.15
    loading: float = 0.5


class SOxRequest(BaseModel):
    gas_flow_nm3_h: float = 50000.0
    SO2_in_ppm: float = 800.0
    SO3_in_ppm: float = 20.0
    scrubber_type: str = 'wet_limestone'


class NOxRequest(BaseModel):
    gas_flow_nm3_h: float = 50000.0
    NO_in_ppm: float = 300.0
    system_type: str = 'scr'


class MercuryRequest(BaseModel):
    gas_flow_nm3_h: float = 50000.0
    Hg_in_ug_Nm3: float = 15.0


@router.post("/vle/equilibrium")
async def get_vle_equilibrium(req: VLERequest):
    vle = CO2AmineVLE(amine=req.amine, concentration_wt=req.concentration_wt)
    P_CO2 = vle.equilibrium_pressure(req.T, req.loading)
    return {
        'amine': req.amine,
        'T': req.T,
        'loading': req.loading,
        'P_CO2_pa': P_CO2,
        'henry_constant': P_CO2 / (req.loading**2),
    }


@router.post("/pollutants/sox")
async def calculate_sox(req: SOxRequest):
    if req.scrubber_type == 'wet_limestone':
        scrubber = WetLimestoneSOxScrubber()
        res = scrubber.calculate_removal(req.gas_flow_nm3_h, req.SO2_in_ppm, req.SO3_in_ppm)
        return {
            'SO2_in': res.SO2_in,
            'SO2_out': res.SO2_out,
            'efficiency': res.removal_efficiency,
            'limestone_consumed_kg_h': res.limestone_consumed,
            'gypsum_produced_kg_h': res.gypsum_produced,
        }
    scrubber = DualAlkaliSOxScrubber()
    return scrubber.calculate_removal(req.gas_flow_nm3_h, req.SO2_in_ppm)


@router.post("/pollutants/nox")
async def calculate_nox(req: NOxRequest):
    if req.system_type == 'scr':
        scr = SCR_System()
        res = scr.calculate_performance(req.gas_flow_nm3_h, req.NO_in_ppm)
        return {
            'NO_in': res.NO_in,
            'NO_out': res.NO_out,
            'efficiency': res.conversion,
            'ammonia_slip_ppm': res.ammonia_slip,
        }
    sncr = SNCR_System()
    return sncr.calculate_performance(req.NO_in_ppm)


@router.post("/pollutants/mercury")
async def calculate_mercury(req: MercuryRequest):
    aci = ActivatedCarbonInjection()
    res = aci.calculate_removal(req.gas_flow_nm3_h, req.Hg_in_ug_Nm3)
    return {
        'Hg_in': res.Hg_in,
        'Hg_out': res.Hg_out,
        'efficiency': res.removal_efficiency,
        'sorbent_consumed_kg_h': res.sorbent_consumed,
    }


@router.post("/plant/simulate")
async def simulate_plant(duration_minutes: float = 10.0):
    plant = CarbonCapturePlant()
    snapshots = []
    n = int(duration_minutes * 6)
    for _ in range(n):
        st = await plant.step(dt=10.0)
        snapshots.append({
            'timestamp': st.timestamp,
            'CO2_capture_efficiency': st.CO2_capture_efficiency,
            'CO2_capture_rate': st.CO2_capture_rate,
            'reboiler_duty': st.reboiler_duty,
        })
    return {'snapshots': snapshots, 'final_efficiency': snapshots[-1]['CO2_capture_efficiency'] if snapshots else 90.0}
