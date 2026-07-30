"""
Sample management with chain-of-custody
"""
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class SampleStatus(str, Enum):
    REGISTERED = "registered"
    IN_STORAGE = "in_storage"
    IN_TEST = "in_test"
    CONSUMED = "consumed"
    DISPOSED = "disposed"
    QUARANTINED = "quarantined"


class HazardClass(str, Enum):
    EXPLOSIVE = "explosive"
    FLAMMABLE = "flammable"
    CORROSIVE = "corrosive"
    TOXIC = "toxic"
    NONE = "none"


@dataclass
class ChainOfCustody:
    timestamp: datetime
    actor: str
    action: str
    location: str
    quantity_used: float = 0.0
    notes: str = ''
    signature_hash: Optional[str] = None


@dataclass
class Sample:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    barcode: str = ''
    chemical_name: str = ''
    cas_number: str = ''
    formula: str = ''
    purity: float = 0.0
    supplier: str = ''
    ghs_class: HazardClass = HazardClass.NONE
    h_statements: List[str] = field(default_factory=list)
    p_statements: List[str] = field(default_factory=list)
    nfpa_health: int = 0
    nfpa_flammability: int = 0
    nfpa_reactivity: int = 0
    storage_location: str = ''
    storage_T: float = 298.15
    initial_quantity: float = 0.0
    current_quantity: float = 0.0
    units: str = 'kg'
    status: SampleStatus = SampleStatus.REGISTERED
    received_by: str = ''
    custody_chain: List[ChainOfCustody] = field(default_factory=list)

    def add_custody_event(self, actor: str, action: str, location: str, quantity_used: float = 0.0, notes: str = '') -> ChainOfCustody:
        event = ChainOfCustody(
            timestamp=datetime.now(),
            actor=actor,
            action=action,
            location=location,
            quantity_used=quantity_used,
            notes=notes,
        )
        prev_hash = self.custody_chain[-1].signature_hash if self.custody_chain else self.id
        content = f"{prev_hash}:{actor}:{action}:{location}:{datetime.now().isoformat()}"
        event.signature_hash = hashlib.sha256(content.encode()).hexdigest()
        self.custody_chain.append(event)
        self.current_quantity -= quantity_used
        return event


class SampleRegistry:
    def __init__(self):
        self.samples: Dict[str, Sample] = {}

    def register(self, sample: Sample) -> Sample:
        self.samples[sample.id] = sample
        return sample

    def get(self, sample_id: str) -> Optional[Sample]:
        return self.samples.get(sample_id)

    def list_active(self) -> List[Sample]:
        return [s for s in self.samples.values() if s.status not in [SampleStatus.DISPOSED, SampleStatus.CONSUMED]]
