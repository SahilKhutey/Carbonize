"""
Shared fixtures for UQ validation tests.
"""

import pytest
import numpy as np

from cbms_sim.domain.uq.sampling import lh_sample
from cbms_sim.domain.uq.sobol import sobol_indices


@pytest.fixture
def rng_seed() -> int:
    """Fixed seed for reproducibility."""
    return 42


@pytest.fixture
def n_samples() -> int:
    """Standard sample count for comparisons."""
    return 1024


@pytest.fixture
def reference_salib():
    """Check if SALib is installed."""
    salib = pytest.importorskip("SALib", reason="SALib not installed")
    return salib
