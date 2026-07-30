"""
Sequential Design of Experiments with Bayesian Optimization
"""
import numpy as np
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass, field
from scipy.optimize import minimize
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)


@dataclass
class BayesianState:
    X_observed: np.ndarray = field(default_factory=list)
    y_observed: np.ndarray = field(default_factory=list)
    iteration: int = 0
    best_x: np.ndarray = None
    best_y: float = -np.inf
    acquisition_history: List[float] = field(default_factory=list)


class GaussianProcessModel:
    def __init__(self, kernel: str = 'rbf', length_scale: float = 1.0, variance: float = 1.0, noise: float = 1e-6):
        self.kernel = kernel
        self.length_scale = length_scale
        self.variance = variance
        self.noise = noise
        self.X_train = None
        self.y_train = None
        self.alpha = None
        self.L = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.X_train = X
        self.y_train = y
        K = self._kernel(X, X) + self.noise * np.eye(len(X))
        try:
            self.L = np.linalg.cholesky(K)
        except np.linalg.LinAlgError:
            K += 1e-5 * np.eye(len(X))
            self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T, np.linalg.solve(self.L, y))

    def predict(self, X: np.ndarray, return_std: bool = True):
        K_star = self._kernel(X, self.X_train)
        mean = K_star @ self.alpha
        if not return_std:
            return mean
        v = np.linalg.solve(self.L, K_star.T)
        K_star_star = self._kernel(X, X)
        var = np.diag(K_star_star) - np.sum(v ** 2, axis=0)
        var = np.maximum(var, 1e-10)
        return mean, np.sqrt(var)

    def _kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        dists = np.sum(X1 ** 2, axis=1)[:, None] + np.sum(X2 ** 2, axis=1)[None, :] - 2 * X1 @ X2.T
        return self.variance * np.exp(-0.5 * np.maximum(dists, 0.0) / (self.length_scale ** 2))


class BayesianOptimizer:
    def __init__(self, objective_fn: Callable, bounds: List[Tuple[float, float]], acquisition: str = 'EI', xi: float = 0.01, maximize: bool = True):
        self.objective_fn = objective_fn
        self.bounds = np.array(bounds)
        self.n_dims = len(bounds)
        self.acquisition = acquisition
        self.xi = xi
        self.maximize = maximize
        self.gp = GaussianProcessModel()
        self.state = BayesianState()

    def initialize(self, n_initial: int = 10):
        from .sampling import LatinHyperCube
        sampler = LatinHyperCube(self.bounds.tolist())
        X = sampler.sample(n_initial)
        y = np.array([self.objective_fn(x) for x in X])
        if not self.maximize:
            y = -y
        self.state.X_observed = X
        self.state.y_observed = y
        best_idx = np.argmax(y)
        self.state.best_x = X[best_idx]
        self.state.best_y = y[best_idx]
        self.state.iteration = n_initial

    def step(self) -> Tuple[np.ndarray, float]:
        self.gp.fit(self.state.X_observed, self.state.y_observed)
        x_next = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
        y_new = float(self.objective_fn(x_next))
        if not self.maximize:
            y_new = -y_new
        self.state.X_observed = np.vstack([self.state.X_observed, x_next])
        self.state.y_observed = np.append(self.state.y_observed, y_new)
        self.state.iteration += 1
        if y_new > self.state.best_y:
            self.state.best_y = y_new
            self.state.best_x = x_next
        return x_next, 0.5

    def run(self, n_iterations: int = 10) -> Dict:
        results = []
        for _ in range(n_iterations):
            x_next, acq = self.step()
            results.append({'x': x_next.tolist(), 'y': float(self.state.best_y)})
        return {'best_x': self.state.best_x.tolist(), 'best_y': float(self.state.best_y), 'history': results}
