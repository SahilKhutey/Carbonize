"""
FastAPI Router for MVP Demo, ROI, & Sales API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from ..demo.seed_data import DemoSeedGenerator
from ..demo.tour_scenarios import get_demo_steps
from ..demo.story_generator import StoryGenerator
from ..roi.calculator import ROICalculator
from ..roi.what_if import WhatIfEngine
from ..architecture.reference import ReferenceArchitecture
from ..architecture.bom import generate_deployment_bom
from ..sales.pitch_deck import get_pitch_deck_slides
from ..sales.loi_template import get_loi_template


router = APIRouter(prefix="/api/v1/mvp", tags=["mvp"])


class ROIRequest(BaseModel):
    capacity_t_yr: float = 1_000_000
    steam_cost_usd_gj: float = 15.0
    solvent_cost_usd_kg: float = 3.50
    co2_tax_credit_usd_t: float = 85.0


@router.get("/demo/seed")
async def get_demo_seed():
    gen = DemoSeedGenerator()
    return {
        'plant': gen.generate_demo_plant(),
        'solvents': gen.generate_top_solvents(),
        'steps': get_demo_steps(),
    }


@router.post("/roi/calculate")
async def calculate_roi(req: ROIRequest):
    calc = ROICalculator()
    result = calc.calculate(
        capacity_t_yr=req.capacity_t_yr,
        steam_cost_usd_gj=req.steam_cost_usd_gj,
        solvent_cost_usd_kg=req.solvent_cost_usd_kg,
        co2_tax_credit_usd_t=req.co2_tax_credit_usd_t,
    )
    what_if = WhatIfEngine()
    result['sensitivity'] = what_if.sensitivity_analysis(req.capacity_t_yr)
    return result


@router.get("/architecture/reference")
async def get_architecture_spec(tier: str = 'medium'):
    return {
        'spec': ReferenceArchitecture.get_tier_spec(tier),
        'bom': generate_deployment_bom(tier),
    }


@router.get("/sales/pitch-deck")
async def get_pitch_deck():
    return {
        'slides': get_pitch_deck_slides(),
        'loi': get_loi_template(),
    }
