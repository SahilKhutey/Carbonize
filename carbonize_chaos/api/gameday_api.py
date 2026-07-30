"""
Game Day API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel
import asyncio
import logging
import time
from chaos_lib.gameday import GameDayEngine, GameDay, GameDayPhase, Inject

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/gameday", tags=["gameday"])

engine = GameDayEngine()


class GameDayCreateRequest(BaseModel):
    name: str
    description: str
    date: str
    duration_minutes: int = 120
    participants: List[Dict] = []
    injects: List[Dict] = []
    notification_channel: str = "#game-days"
    meeting_link: Optional[str] = None


class ActionRecordRequest(BaseModel):
    participant_id: str
    inject_id: Optional[str] = None
    action_type: str
    description: str
    time_to_detect_seconds: Optional[int] = None
    quality: Optional[int] = None
    verified: Optional[bool] = None


@router.post("/create")
async def create_gameday(req: GameDayCreateRequest):
    """Create a new game day."""
    gameday = GameDay(
        id=f"gd_{req.date.replace('-', '')}_{req.name[:10]}",
        name=req.name,
        description=req.description,
        date=req.date,
        duration_minutes=req.duration_minutes,
        participants=[],
        injects=[],
        phases=[GameDayPhase.INTRO, GameDayPhase.DETECTION, GameDayPhase.TRIAGE, GameDayPhase.MITIGATION, GameDayPhase.RESOLUTION, GameDayPhase.POSTMORTEM],
        notification_channel=req.notification_channel,
        meeting_link=req.meeting_link,
    )
    engine.gamedays[gameday.id] = gameday
    return {'id': gameday.id, 'name': gameday.name}


@router.get("/list")
async def list_gamedays():
    """List all game days."""
    return [
        {
            'id': g.id,
            'name': g.name,
            'date': g.date,
            'duration_minutes': g.duration_minutes,
            'participants': len(g.participants),
            'injects': len(g.injects),
        }
        for g in engine.gamedays.values()
    ]


@router.post("/{gameday_id}/run")
async def run_gameday(gameday_id: str, background_tasks: BackgroundTasks):
    """Start a game day (runs in background)."""
    if gameday_id not in engine.gamedays:
        raise HTTPException(404, f"Game day {gameday_id} not found")
    background_tasks.add_task(engine.run_gameday, gameday_id)
    return {
        'status': 'running',
        'gameday_id': gameday_id,
        'meeting_link': engine.gamedays[gameday_id].meeting_link,
    }


@router.post("/{gameday_id}/action")
async def record_action(gameday_id: str, action: ActionRecordRequest):
    """Record an action taken by a participant."""
    if gameday_id not in engine.gamedays:
        raise HTTPException(404, f"Game day {gameday_id} not found")
    await engine.record_action(action.participant_id, action.dict())
    return {'status': 'recorded'}


@router.get("/{gameday_id}/status")
async def get_gameday_status(gameday_id: str):
    """Get current game day status."""
    if gameday_id not in engine.gamedays:
        raise HTTPException(404, f"Game day {gameday_id} not found")
    gameday = engine.gamedays[gameday_id]
    return {
        'id': gameday.id,
        'name': gameday.name,
        'current_phase': gameday.current_phase.value,
        'started_at': gameday.started_at or time.time(),
        'completed_at': gameday.completed_at,
        'injects_completed': sum(1 for i in gameday.injects if i.status.value == 'completed'),
        'injects_total': len(gameday.injects),
    }
