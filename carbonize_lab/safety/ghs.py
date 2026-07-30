"""
GHS Hazard Classification
"""
from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum


class GHSPictogram(str, Enum):
    EXPLOSIVE = "GHS01"
    FLAMMABLE = "GHS02"
    OXIDIZING = "GHS03"
    GAS_UNDER_PRESSURE = "GHS04"
    CORROSIVE = "GHS05"
    ACUTE_TOXICITY = "GHS06"
    HEALTH_HAZARD = "GHS08"
    ENVIRONMENTAL = "GHS09"


@dataclass
class GHSClassification:
    cas_number: str
    name: str
    pictograms: List[GHSPictogram] = field(default_factory=list)
    signal_word: str = ''
    h_statements: List[str] = field(default_factory=list)
    p_statements: List[str] = field(default_factory=list)


KNOWN_CLASSIFICATIONS = {
    '141-43-5': GHSClassification(
        cas_number='141-43-5', name='Monoethanolamine',
        pictograms=[GHSPictogram.CORROSIVE, GHSPictogram.HEALTH_HAZARD], signal_word='Danger',
        h_statements=['H302: Harmful if swallowed', 'H314: Causes severe skin burns and eye damage'],
        p_statements=['P260: Do not breathe dust/fume', 'P280: Wear protective gloves'],
    ),
    '105-59-9': GHSClassification(
        cas_number='105-59-9', name='Methyldiethanolamine',
        pictograms=[GHSPictogram.HEALTH_HAZARD], signal_word='Warning',
        h_statements=['H319: Causes serious eye irritation'],
        p_statements=['P280: Wear eye protection'],
    ),
    '110-85-0': GHSClassification(
        cas_number='110-85-0', name='Piperazine',
        pictograms=[GHSPictogram.CORROSIVE, GHSPictogram.HEALTH_HAZARD], signal_word='Danger',
        h_statements=['H314: Causes severe skin burns', 'H334: May cause respiratory sensitization'],
        p_statements=['P261: Avoid breathing dust'],
    ),
}


def get_classification(cas: str) -> GHSClassification:
    return KNOWN_CLASSIFICATIONS.get(cas, GHSClassification(cas_number=cas, name='Unknown'))
