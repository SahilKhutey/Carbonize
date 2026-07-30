"""
Chaos engineering API
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional
from pydantic import BaseModel
import asyncio
import logging

from chaos_lib.orchestrator import ChaosOrchestrator, ChaosExperiment


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/chaos", tags=["chaos"])

orchestrator = ChaosOrchestrator()


class ExperimentRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    duration: int = 60
    probes: List[Dict]
    steady_state_checks: List[Dict] = []
    blast_radius: Dict = {}
    abort_conditions: List[Dict] = []
    tags: Dict = {}


@router.post("/experiments")
async def create_experiment(req: ExperimentRequest):
    """Create a new experiment from definition."""
    experiment = ChaosExperiment(
        name=req.name,
        description=req.description or "",
        hypothesis=req.description or "",
        probes=req.probes,
        steady_state_checks=req.steady_state_checks,
        duration=req.duration,
        blast_radius=req.blast_radius,
        abort_conditions=req.abort_conditions,
        tags=req.tags,
    )
    orchestrator.experiments[experiment.name] = experiment
    return {'status': 'created', 'name': experiment.name}


@router.get("/experiments")
async def list_experiments():
    """List all defined experiments."""
    return {
        'experiments': [
            {
                'name': e.name,
                'description': e.description,
                'duration': e.duration,
                'probes': len(e.probes),
                'tags': e.tags,
            }
            for e in orchestrator.experiments.values()
        ]
    }


@router.post("/experiments/{name}/run")
async def run_experiment(name: str):
    """Run a specific experiment."""
    if name not in orchestrator.experiments:
        raise HTTPException(404, f"Experiment {name} not found")
    
    result = await orchestrator.run_experiment(name)
    return {
        'experiment_name': result.experiment_name,
        'status': result.status.value,
        'hypothesis_validated': result.hypothesis_validated,
        'resilience_score': result.resilience_score,
        'slo_violations': result.total_slo_violations,
        'recovery_time': result.recovery_time_seconds,
    }


@router.get("/results")
async def list_results():
    """List all experiment results."""
    return {
        'results': [
            {
                'experiment_name': r.experiment_name,
                'status': r.status.value,
                'hypothesis_validated': r.hypothesis_validated,
                'resilience_score': r.resilience_score,
                'started_at': r.started_at,
                'completed_at': r.completed_at,
            }
            for r in orchestrator.results
        ]
    }


@router.post("/safety/global-abort")
async def global_abort():
    """Trigger global abort of all chaos experiments."""
    orchestrator.safety.global_abort()
    return {'status': 'aborted'}


@router.post("/safety/reset")
async def reset_safety():
    """Reset safety state."""
    orchestrator.safety.reset()
    return {'status': 'reset'}
