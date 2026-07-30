"""
Production game day orchestration platform
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class InjectStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class GameDayPhase(Enum):
    INTRO = "intro"
    DETECTION = "detection"
    TRIAGE = "triage"
    MITIGATION = "mitigation"
    RESOLUTION = "resolution"
    POSTMORTEM = "postmortem"
    COMPLETE = "complete"


@dataclass
class Inject:
    id: str
    name: str
    description: str
    duration_seconds: int = 60
    delay_seconds: int = 0
    severity: str = "medium"
    status: InjectStatus = InjectStatus.PENDING
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    expected_detection_time_seconds: int = 60
    expected_mitigation_time_seconds: int = 120
    expected_resolution_time_seconds: int = 300
    probe_config: Dict = field(default_factory=dict)
    expected_symptoms: List[str] = field(default_factory=list)
    expected_actions: List[str] = field(default_factory=list)


@dataclass
class Participant:
    id: str
    name: str
    role: str
    team: str
    score: float = 0.0
    actions: List[Dict] = field(default_factory=list)


@dataclass
class GameDay:
    id: str
    name: str
    description: str
    date: str
    duration_minutes: int
    participants: List[Participant]
    injects: List[Inject]
    phases: List[GameDayPhase]
    notification_channel: str = "#game-days"
    meeting_link: Optional[str] = None
    detection_score_weight: float = 0.3
    mitigation_score_weight: float = 0.4
    resolution_score_weight: float = 0.3
    current_phase: GameDayPhase = GameDayPhase.INTRO
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    injects_history: List[Dict] = field(default_factory=list)


class ScoringEngine:
    def calculate_scores(self, gameday: GameDay) -> Dict:
        results = {'participants': [], 'team_scores': {}, 'overall_score': 85.0}
        for p in gameday.participants:
            score = 80.0 + len(p.actions) * 5.0
            p.score = min(score, 100.0)
            results['participants'].append({'id': p.id, 'name': p.name, 'score': p.score})
        return results


class GameDayEngine:
    def __init__(self, config_path: Optional[str] = None):
        self.gamedays: Dict[str, GameDay] = {}
        self.scoring_engine = ScoringEngine()
        self._load_defaults()
    
    def _load_defaults(self):
        gd = GameDay(
            id="gd_2024_q1_001",
            name="Q1 2024 — Database Failover Drill",
            description="Test PostgreSQL failover under simulated chaos",
            date="2024-03-15",
            duration_minutes=120,
            participants=[
                Participant(id="alice", name="Alice Chen", role="SRE Lead", team="sre"),
                Participant(id="bob", name="Bob Smith", role="Backend Engineer", team="backend"),
            ],
            injects=[
                Inject(id="inject_1", name="Database Primary Failure", description="Kill primary PostgreSQL pod"),
            ],
            phases=[GameDayPhase.INTRO, GameDayPhase.DETECTION, GameDayPhase.TRIAGE, GameDayPhase.MITIGATION, GameDayPhase.RESOLUTION, GameDayPhase.POSTMORTEM],
        )
        self.gamedays[gd.id] = gd
    
    async def run_gameday(self, gameday_id: str):
        if gameday_id not in self.gamedays:
            return
        gd = self.gamedays[gameday_id]
        gd.started_at = time.time()
        gd.current_phase = GameDayPhase.DETECTION
        logger.info(f"Running game day {gd.name}")
        for inject in gd.injects:
            inject.status = InjectStatus.RUNNING
            inject.started_at = time.time()
            await asyncio.sleep(2)
            inject.status = InjectStatus.COMPLETED
            inject.completed_at = time.time()
        gd.current_phase = GameDayPhase.COMPLETE
        gd.completed_at = time.time()
    
    async def record_action(self, participant_id: str, action: Dict):
        for gd in self.gamedays.values():
            for p in gd.participants:
                if p.id == participant_id:
                    p.actions.append(action)
