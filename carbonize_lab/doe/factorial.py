"""
Factorial, Fractional Factorial, CCD, Box-Behnken, and Plackett-Burman Designs
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from itertools import product
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExperimentalFactor:
    name: str
    low: float
    high: float
    units: str = ''
    center: float = None

    def __post_init__(self):
        if self.center is None:
            self.center = 0.5 * (self.low + self.high)


class FullFactorial:
    def __init__(self, factors: List[ExperimentalFactor]):
        self.factors = factors
        self.k = len(factors)
        self.n_runs = 2 ** self.k

    def design(self, n_center: int = 0, n_replicates: int = 1) -> np.ndarray:
        levels = np.array([[-1, 1] for _ in range(self.k)])
        grid = np.array(list(product(*levels)))
        if n_replicates > 1:
            grid = np.tile(grid, (n_replicates, 1))
        if n_center > 0:
            centers = np.zeros((n_center, self.k))
            grid = np.vstack([grid, centers])

        actual = np.zeros_like(grid, dtype=float)
        for i, factor in enumerate(self.factors):
            actual[:, i] = (grid[:, i] + 1) / 2 * (factor.high - factor.low) + factor.low
        return actual


class FractionalFactorial:
    def __init__(self, factors: List[ExperimentalFactor], resolution: int = 4):
        self.factors = factors
        self.k = len(factors)
        self.resolution = resolution

    def design(self, generator: str = 'auto') -> np.ndarray:
        full = FullFactorial(self.factors).design()
        return full[::2]


class CentralComposite:
    def __init__(self, factors: List[ExperimentalFactor]):
        self.factors = factors
        self.k = len(factors)
        self.alpha = (2 ** self.k) ** 0.25

    def design(self, n_center: int = 5, alpha: float = None) -> np.ndarray:
        if alpha is None:
            alpha = self.alpha
        levels = np.array([-1, 1])
        factorial = np.array(list(product(*[levels] * self.k)))
        axial = np.zeros((2 * self.k, self.k))
        for i in range(self.k):
            axial[2*i, i] = -alpha
            axial[2*i+1, i] = alpha
        centers = np.zeros((n_center, self.k))
        designs = np.vstack([factorial, axial, centers])

        actual = np.zeros_like(designs, dtype=float)
        for i, factor in enumerate(self.factors):
            center = (factor.high + factor.low) / 2
            half_range = (factor.high - factor.low) / 2
            actual[:, i] = designs[:, i] * half_range + center
        return actual


class BoxBehnken:
    def __init__(self, factors: List[ExperimentalFactor]):
        self.factors = factors
        self.k = len(factors)

    def design(self, n_center: int = 3) -> np.ndarray:
        if self.k < 3:
            raise ValueError("Box-Behnken requires at least 3 factors")
        n_runs = 2 * self.k * (self.k - 1) + n_center
        actual = np.zeros((n_runs, self.k), dtype=float)
        run_idx = 0
        for i in range(self.k):
            for j in range(i + 1, self.k):
                for sign in [-1, 1]:
                    actual[run_idx, i] = sign
                    actual[run_idx, j] = sign
                    run_idx += 1
        for _ in range(n_center):
            actual[run_idx] = 0.0
            run_idx += 1

        for i, factor in enumerate(self.factors):
            center = (factor.high + factor.low) / 2
            half_range = (factor.high - factor.low) / 2
            actual[:, i] = actual[:, i] * half_range + center
        return actual


class PlackettBurman:
    def __init__(self, factors: List[ExperimentalFactor]):
        self.factors = factors
        self.k = len(factors)

    def design(self) -> np.ndarray:
        n_runs = self.k + 1
        H = np.ones((n_runs, self.k), dtype=float)
        for i in range(n_runs):
            H[i, i % self.k] = -1.0

        actual = np.zeros_like(H, dtype=float)
        for i, factor in enumerate(self.factors):
            actual[:, i] = (H[:, i] + 1) / 2 * (factor.high - factor.low) + factor.low
        return actual
