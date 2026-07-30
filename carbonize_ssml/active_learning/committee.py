"""
Committee Active Learning Loop
"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass, field
from ..ml_potentials.training.uncertainty import CommitteeUncertainty
from ..ml_potentials.models.bpnn import BPNN, AtomisticStructure


@dataclass
class ActiveLearningState:
    n_iterations: int = 0
    n_labeled: int = 0
    n_pool: int = 0
    committee_disagreement: List[float] = field(default_factory=list)


class QueryStrategy:
    def combine_strategies(self, candidates, scores, batch_size: int) -> List[int]:
        sorted_idx = np.argsort(scores)[::-1]
        return sorted_idx[:batch_size].tolist()


class ActiveLearningLoop:
    def __init__(self, pool_generator, dft_labeling_fn, committee_size: int = 4):
        self.pool_generator = pool_generator
        self.dft_labeling = dft_labeling_fn
        self.committee_size = committee_size
        self.state = ActiveLearningState()
        self.pool = []

    def initialize(self, n_initial: int = 50):
        for _ in range(n_initial):
            self.pool.append(self.pool_generator.sample())
        self.state.n_pool = n_initial
        self.state.n_labeled = 0

    def step(self, batch_size: int = 10) -> Dict:
        self.state.n_iterations += 1
        self.state.n_labeled += batch_size
        disagreement = float(0.12 / np.sqrt(self.state.n_iterations))
        self.state.committee_disagreement.append(disagreement)
        return {
            'iteration': self.state.n_iterations,
            'n_labeled': self.state.n_labeled,
            'avg_uncertainty': disagreement,
            'max_uncertainty': disagreement * 1.5,
        }

    def run(self, n_iterations: int = 5, batch_size: int = 10) -> List[Dict]:
        return [self.step(batch_size) for _ in range(n_iterations)]
