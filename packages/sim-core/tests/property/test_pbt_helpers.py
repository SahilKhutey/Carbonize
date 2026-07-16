"""
Custom helpers for property-based tests.
"""

def params_residence(params: dict) -> float:
    """Get a reasonable t_span max from params (for testing)."""
    return 100.0  # 100 seconds default
