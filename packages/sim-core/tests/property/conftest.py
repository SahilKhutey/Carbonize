"""
Configuration for property-based testing with Hypothesis.
"""

import os
from hypothesis import settings, Verbosity, HealthCheck, Phase

# Detect if running in CI
is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("RUN_FULL_FUZZ") == "true"

# Default settings: 10K examples per test (DoD requirement in CI)
default_settings = settings(
    max_examples=10_000 if is_ci else 100,
    deadline=120_000 if is_ci else 10_000,
    derandomize=True,        # Deterministic for CI reproducibility
    print_blob=True,          # Show failing example in CI logs
    verbosity=Verbosity.normal,
    
    # Disable slow health checks (they're too strict for ODE testing)
    suppress_health_check=[
        HealthCheck.too_slow,        # Some ODE solves are inherently slow
        HealthCheck.data_too_large,  # Big state vectors are fine
        HealthCheck.filter_too_much,
    ],
    
    # Phases: prioritize example collection
    phases=tuple(Phase),  # All phases
)

# Stricter settings for critical properties
strict_settings = settings(
    max_examples=50_000 if is_ci else 200,
    deadline=240_000 if is_ci else 20_000,
    derandomize=True,
)

# Quick settings for development (not CI)
dev_settings = settings(
    max_examples=100,
    deadline=10_000,
    derandomize=True,
)

# Settings for CI (explicit, no surprise)
ci_settings = settings(
    max_examples=10_000 if is_ci else 100,  # DoD: 10K random valid inputs
    deadline=120_000 if is_ci else 10_000,
    derandomize=True,
    print_blob=True,
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
        HealthCheck.filter_too_much,
    ],
)
