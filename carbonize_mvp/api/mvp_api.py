"""
FastAPI Router for MVP Demo, ROI, & Sales API
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np

from ..demo.seed_data import DemoSeedData
from ..demo.tour_scenarios import get_demo_steps
from ..demo.story_generator import StoryGenerator
from ..roi.calculator import ROICalculator
from ..roi.what_if import WhatIfEngine
from ..architecture.reference import ReferenceArchitecture
from ..architecture.bom import generate_deployment_bom
from ..sales.pitch_deck import get_pitch_deck_slides
from ..sales.loi_template import get_loi_template


router = APIRouter(prefix="/api/v1/demo", tags=["demo"])

# Cache seed data once
SEED = {
    'solvents': DemoSeedData.generate_solvent_portfolio(),
    'operations': DemoSeedData.generate_plant_operations(12),
    'lab_results': DemoSeedData.generate_lab_results(),
    'chaos_drills': DemoSeedData.generate_chaos_drill_results(),
    'roi_scenarios': DemoSeedData.generate_roi_scenarios(),
    'comparison': DemoSeedData.generate_loader_comparison(),
    'pilot_proposal': DemoSeedData.generate_pilot_proposal(),
}


class ROIRequest(BaseModel):
    capacity_tons_per_year: float = 500_000
    current_solvent: str = 'MEA'
    current_opex_per_ton_usd: float = 60.0
    current_energy_gj_per_ton: float = 4.2
    recommended_solvent: str = 'SOLV-0237'
    discount_rate: float = 0.08
    plant_lifetime_years: int = 10


@router.get("/overview")
async def demo_overview():
    return {
        'company': 'Carbonize',
        'tagline': 'AI-designed chemistry for industrial carbon capture',
        'metrics': {
            'solvents_screened': len(SEED['solvents']),
            'best_solvent_score': max(s['overall_score'] for s in SEED['solvents']),
            'solvents_synthesized': sum(1 for s in SEED['solvents'] if s['synthesized']),
            'lab_validated': sum(1 for s in SEED['solvents'] if s['lab_tested']),
            'avg_prediction_accuracy': 92.4,
            'chaos_drills_completed': len(SEED['chaos_drills']),
            'avg_resilience_score': sum(d['resilience_score'] for d in SEED['chaos_drills']) / len(SEED['chaos_drills']),
            'largest_pilot_savings_usd': 26_000_000,
        },
        'hero_candidate': {
            'name': 'SOLV-0237',
            'improvement_vs_mea': {
                'energy_reduction': 0.32,
                'capacity_improvement': 0.18,
                'degradation_reduction': 0.85,
            },
        },
    }


@router.get("/solvents")
async def list_solvents(sort_by: str = 'overall_score', order: str = 'desc', limit: int = 100):
    solvents = SEED['solvents']
    sorted_solvents = sorted(solvents, key=lambda s: s.get(sort_by, 0), reverse=(order == 'desc'))
    return {'total': len(sorted_solvents), 'solvents': sorted_solvents[:limit]}


@router.get("/solvents/{solvent_id}")
async def get_solvent(solvent_id: str):
    solvents = [s for s in SEED['solvents'] if s['id'] == solvent_id]
    if not solvents:
        raise HTTPException(404, f"Solvent {solvent_id} not found")
    solvent = solvents[0]
    if solvent.get('is_hero'):
        solvent['story'] = {
            'why_special': 'Discovered through AI screening of 12,000 candidates. Combines high capacity with low regeneration energy.',
            'lab_results': [r for r in SEED['lab_results'] if r['solvent'] == solvent_id],
            'comparison_vs_mea': {
                'energy_reduction_percent': 27,
                'capacity_improvement_percent': 18,
                'degradation_reduction_percent': 88,
                'predicted_annual_savings_large_plant': 26_000_000,
            },
        }
    return solvent


@router.get("/solvents/{solvent_id}/compare/{baseline_id}")
async def compare_solvents(solvent_id: str, baseline_id: str):
    solvents = {s['id']: s for s in SEED['solvents']}
    if solvent_id not in solvents: raise HTTPException(404, f"Solvent {solvent_id} not found")
    if baseline_id not in solvents: raise HTTPException(404, f"Baseline {baseline_id} not found")
    s = solvents[solvent_id]
    b = solvents[baseline_id]
    return {
        'solvent': s,
        'baseline': b,
        'improvements': {
            'energy_reduction_percent': (b['heat_of_absorption_kj_mol'] - s['heat_of_absorption_kj_mol']) / b['heat_of_absorption_kj_mol'] * 100,
            'capacity_improvement_percent': (s['co2_loading_max'] - b['co2_loading_max']) / b['co2_loading_max'] * 100,
            'rate_improvement_percent': (s['absorption_rate_1_s'] - b['absorption_rate_1_s']) / b['absorption_rate_1_s'] * 100,
            'degradation_reduction_percent': (b['degradation_rate_per_year'] - s['degradation_rate_per_year']) / b['degradation_rate_per_year'] * 100,
        },
    }


@router.get("/operations")
async def plant_operations(days: int = 30):
    ops = SEED['operations'][-days:]
    return {
        'days': days,
        'data': ops,
        'stats': {
            'avg_capture_tons_per_day': sum(o['co2_capture_tons'] for o in ops) / len(ops),
            'avg_efficiency': sum(o['capture_efficiency'] for o in ops) / len(ops),
            'total_anomalies': sum(1 for o in ops if o['anomaly_detected']),
            'total_chaos_events': sum(1 for o in ops if o['chaos_event']),
        },
    }


@router.get("/lab-results")
async def lab_results():
    return {'results': SEED['lab_results'], 'summary': {'avg_loading_error': 0.85, 'r_squared_loading': 0.97}}


@router.get("/chaos-results")
async def chaos_results():
    total_savings = sum(d['cost_savings_usd'] for d in SEED['chaos_drills'])
    total_downtime = sum(d['downtime_avoided_hours'] for d in SEED['chaos_drills'])
    return {
        'drills': SEED['chaos_drills'],
        'summary': {
            'total_drills': len(SEED['chaos_drills']),
            'total_cost_savings_usd': total_savings,
            'total_downtime_avoided_hours': total_downtime,
            'avg_detection_time_min': 2.6,
            'avg_baseline_detection_min': 45.0,
            'detection_speedup_factor': 17.3,
            'avg_resilience_score': 94.3,
        },
    }


@router.post("/roi/calculate")
async def calculate_roi(req: ROIRequest):
    calc = ROICalculator()
    res = calc.calculate(capacity_t_yr=req.capacity_tons_per_year, steam_cost_usd_gj=15.0)
    return {
        'inputs': {'capacity_tons_per_year': req.capacity_tons_per_year, 'current_solvent': req.current_solvent, 'recommended_solvent': req.recommended_solvent},
        'current_state': {'opex_per_ton_usd': req.current_opex_per_ton_usd, 'energy_gj_per_ton': req.current_energy_gj_per_ton, 'annual_opex_usd': req.current_opex_per_ton_usd * req.capacity_tons_per_year},
        'projected_state': {'opex_per_ton_usd': req.current_opex_per_ton_usd * 0.7, 'energy_gj_per_ton': req.current_energy_gj_per_ton * 0.68, 'annual_opex_usd': req.current_opex_per_ton_usd * 0.7 * req.capacity_tons_per_year},
        'savings': {'annual_opex_savings_usd': res['annual_savings_usd'], 'opex_reduction_percent': 30.0, 'energy_reduction_percent': 32.0},
        'investment': {'implementation_cost_usd': res['retrofitting_capex_usd'], 'payback_period_months': res['payback_months'], 'ten_year_npv_usd': res['npv_10yr_usd'], 'cash_flows': [{'year': i, 'cumulative': res['annual_savings_usd']*i - res['retrofitting_capex_usd']} for i in range(1, 11)]},
        'impact': {'co2_avoided_per_year_tons': req.capacity_tons_per_year * 0.05, 'equivalent_cars_off_road': (req.capacity_tons_per_year * 0.05) / 4.6},
    }


@router.get("/comparison")
async def carbonize_vs_traditional():
    return SEED['comparison']


@router.get("/proposal")
async def pilot_proposal():
    return SEED['pilot_proposal']


@router.get("/tour/steps")
async def tour_steps():
    return {'steps': get_demo_steps()}
