"""
HAZOP & LOPA Analysis
"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    SAFETY = "safety"
    OPERABILITY = "operability"
    ENVIRONMENTAL = "environmental"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HAZOPNode:
    parameter: str
    deviation: str
    causes: List[str]
    consequences: List[str]
    safeguards: List[str]
    recommendations: List[str]
    severity: Severity = Severity.SAFETY
    likelihood: int = 1
    severity_score: int = 1
    risk: RiskLevel = RiskLevel.LOW

    def compute_risk(self):
        score = self.severity_score * self.likelihood
        if score <= 4: self.risk = RiskLevel.LOW
        elif score <= 9: self.risk = RiskLevel.MEDIUM
        elif score <= 15: self.risk = RiskLevel.HIGH
        else: self.risk = RiskLevel.CRITICAL


class HAZOPStudy:
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.nodes: List[HAZOPNode] = []

    def add_node(self, node: HAZOPNode):
        node.compute_risk()
        self.nodes.append(node)


class CO2AbsorptionHAZOP(HAZOPStudy):
    def __init__(self):
        super().__init__('CO2_Absorber_Column')
        self.add_node(HAZOPNode(
            parameter='temperature', deviation='high',
            causes=['Heat exchanger failure', 'Hot gas feed'],
            consequences=['Amine degradation', 'Solvent loss'],
            safeguards=['Temperature alarms', 'High-T shutdown'],
            recommendations=['Add redundant T sensors'],
            severity=Severity.SAFETY, likelihood=2, severity_score=4,
        ))
        self.add_node(HAZOPNode(
            parameter='solvent_flow', deviation='low',
            causes=['Pump failure', 'Blockage'],
            consequences=['Reduced CO2 capture'],
            safeguards=['Low-flow alarm'],
            recommendations=['Redundant pump'],
            severity=Severity.OPERABILITY, likelihood=3, severity_score=3,
        ))
        self.add_node(HAZOPNode(
            parameter='CO2_pressure', deviation='high',
            causes=['Blockage downstream'],
            consequences=['Vessel rupture'],
            safeguards=['PSV'],
            recommendations=['Test PSV quarterly'],
            severity=Severity.SAFETY, likelihood=1, severity_score=5,
        ))


class LOPA:
    def __init__(self, scenario: str):
        self.scenario = scenario
        self.initiating_event_freq = 1.0
        self.IPL_layers: List[Dict] = []

    def add_IPL(self, name: str, PFD: float, description: str = ''):
        self.IPL_layers.append({'name': name, 'PFD': PFD, 'description': description})

    def compute_safety_integrity_level(self) -> Dict:
        overall_PFD = self.initiating_event_freq
        for layer in self.IPL_layers:
            overall_PFD *= layer['PFD']
        if overall_PFD >= 1e-1: sil = 'SIL 0'
        elif overall_PFD >= 1e-2: sil = 'SIL 1'
        elif overall_PFD >= 1e-3: sil = 'SIL 2'
        elif overall_PFD >= 1e-4: sil = 'SIL 3'
        else: sil = 'SIL 4'
        return {'initiating_event_freq': self.initiating_event_freq, 'layers': self.IPL_layers, 'overall_PFD': float(overall_PFD), 'SIL': sil}
