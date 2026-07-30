"""
Automated Hypothesis Generation for Closed-Loop Discovery
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from .knowledge_base import KnowledgeBase
import logging

logger = logging.getLogger(__name__)


@dataclass
class Hypothesis:
    id: str
    statement: str
    rationale: str
    predicted_outcome: Dict
    experiment_design: Dict
    prior_probability: float = 0.5
    testable: bool = True
    source: str = ''
    tested: bool = False
    test_result: Optional[bool] = None
    confidence: float = 0.5


class HypothesisGenerator:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base

    def generate_from_data(self, data: Dict, features: List[str]) -> List[Hypothesis]:
        hypotheses = []
        results = data.get('results', [])
        correlations = {}
        for i, f1 in enumerate(features):
            for f2 in features[i + 1:]:
                x = [r.get(f1, 0) for r in results]
                y = [r.get(f2, 0) for r in results]
                if len(x) > 3 and np.std(x) > 0 and np.std(y) > 0:
                    corr = float(np.corrcoef(x, y)[0, 1])
                    if abs(corr) > 0.5:
                        correlations[(f1, f2)] = corr

        for (f1, f2), corr in correlations.items():
            direction = 'positively' if corr > 0 else 'negatively'
            hypotheses.append(Hypothesis(
                id=f"h_corr_{f1}_{f2}",
                statement=f"{f1} is {direction} correlated with {f2}",
                rationale=f"Observed correlation r={corr:.2f} in dataset",
                predicted_outcome={f1: 'increase', f2: 'change'},
                experiment_design={'type': 'factorial', 'factors': [f1, f2]},
                prior_probability=0.6,
                source='data-driven',
            ))

        if not hypotheses:
            hypotheses.append(Hypothesis(
                id="h_default_1",
                statement="Increasing amine concentration increases CO2 loading capacity linearly",
                rationale="Standard zwitterion mechanism reaction order",
                predicted_outcome={'loading': 'increase'},
                experiment_design={'type': 'full_factorial', 'factors': ['concentration', 'temperature']},
                prior_probability=0.75,
                source='domain-knowledge',
            ))
        return hypotheses
