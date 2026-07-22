"""Reaction kinetics solver.

The 9-species legacy engine (engine.py) has been retired.
ExtendedKineticsEngine (17-species, NOx-aware) is the single source of truth.
KineticsEngine and solve_kinetics are kept as stable public aliases.
"""

from cbms_sim.domain.kinetics.extended_engine import (
    ExtendedKineticsEngine,
    ExtendedKineticsConfig as KineticsConfig,
)
from cbms_sim.domain.kinetics.kernels import reaction_rhs_numba
from cbms_sim.domain.models.results import KineticsResult

# Stable public alias – all callers that use `KineticsEngine` get the extended solver.
KineticsEngine = ExtendedKineticsEngine


def solve_kinetics(plant, reagent, conditions, config=None):
    """Convenience wrapper: run ExtendedKineticsEngine with optional config override."""
    engine = ExtendedKineticsEngine(config=config or KineticsConfig())
    return engine.solve(plant, reagent, conditions)


__all__ = [
    "KineticsEngine",
    "KineticsConfig",
    "ExtendedKineticsEngine",
    "solve_kinetics",
    "KineticsResult",
    "reaction_rhs_numba",
]
