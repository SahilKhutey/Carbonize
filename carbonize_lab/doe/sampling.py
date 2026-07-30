"""
Space-Filling Sampling Designs (Latin Hypercube & Sobol)
"""
import numpy as np
from typing import List, Tuple
from scipy.stats import qmc
from scipy.spatial.distance import pdist


class LatinHyperCube:
    def __init__(self, bounds: List[Tuple[float, float]]):
        self.bounds = np.array(bounds)
        self.n_dims = len(bounds)

    def sample(self, n_samples: int, criterion: str = 'maximin') -> np.ndarray:
        sampler = qmc.LatinHypercube(d=self.n_dims)
        samples = sampler.random(n=n_samples)
        return qmc.scale(samples, self.bounds[:, 0], self.bounds[:, 1])


class SobolSampling:
    def __init__(self, bounds: List[Tuple[float, float]]):
        self.bounds = np.array(bounds)
        self.n_dims = len(bounds)

    def sample(self, n_samples: int, seed: int = 42, scramble: bool = True) -> np.ndarray:
        sampler = qmc.Sobol(d=self.n_dims, scramble=scramble, seed=seed)
        m = int(np.ceil(np.log2(n_samples)))
        samples = sampler.random_base2(m=m)
        return qmc.scale(samples[:n_samples], self.bounds[:, 0], self.bounds[:, 1])
