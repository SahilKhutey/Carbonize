"""
Electronic Lab Notebook (ELN) & Standard Operating Procedures (SOPs)
"""
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ExperimentStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ExperimentType(str, Enum):
    ABSORPTION = "absorption"
    ADSORPTION = "adsorption"
    CATALYSIS = "catalysis"
    ANALYSIS = "analysis"


@dataclass
class Step:
    step_number: int
    description: str
    duration_min: float = 0.0
    temperature: float = 298.15
    safety_notes: str = ''


@dataclass
class Measurement:
    timestamp: datetime
    measurement_type: str
    value: float
    units: str
    instrument: str = ''


@dataclass
class Experiment:
    id: str = ''
    title: str = ''
    objective: str = ''
    experiment_type: ExperimentType = ExperimentType.ABSORPTION
    status: ExperimentStatus = ExperimentStatus.PLANNED
    researcher: str = ''
    sop_reference: str = ''
    steps: List[Step] = field(default_factory=list)
    measurements: List[Measurement] = field(default_factory=list)
    content_hash: str = ''

    def compute_hash(self) -> str:
        content = json.dumps({'id': self.id, 'title': self.title, 'type': self.experiment_type}, sort_keys=True)
        self.content_hash = hashlib.sha256(content.encode()).hexdigest()
        return self.content_hash


class SOP:
    def __init__(self, name: str, version: str = '1.0'):
        self.name = name
        self.version = version
        self.procedure: List[Dict] = []
        self.warnings: List[str] = []
        self.hazard_analysis: Dict = {}

    def add_step(self, step_number: int, description: str, duration_min: float, safety: str = ''):
        self.procedure.append({'step_number': step_number, 'description': description, 'duration_min': duration_min, 'safety': safety})


class CO2AbsorptionSOP(SOP):
    def __init__(self):
        super().__init__('CO2_Absorption_Measurement', '2.0')
        self.hazard_analysis = {'amines': 'Corrosive, toxic — use fume hood', 'CO2': 'Asphyxiant'}
        self.add_step(1, 'Set up gas absorption rig', 30, 'Leak check with snoop test')
        self.add_step(2, 'Weigh 100 g amine solution into absorber', 5, 'Use PPE gloves, goggles')
        self.add_step(3, 'Set temperature to operating condition', 15, 'Verify T before gas flow')
        self.add_step(4, 'Begin CO2 gas flow at 100 mL/min', 5, 'Monitor flow rate')
        self.add_step(5, 'Record weight gain every 5 minutes', 60, 'Track loading vs time')


class ViscosityMeasurementSOP(SOP):
    def __init__(self):
        super().__init__('Viscosity_Measurement', '1.5')
        self.add_step(1, 'Calibrate viscometer with standard oil', 30, 'Recalibrate if T changes')
        self.add_step(2, 'Measure viscosity at 100 rpm', 5, 'Repeat 3 times')
