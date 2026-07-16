"""
Centralized rate limit configuration.

All limits are documented with rationale. Modify with care.
"""

from enum import Enum


class RateLimitTier(str, Enum):
    """Rate limit tiers based on endpoint criticality."""
    
    AUTH = "auth"             # Authentication endpoints (strict)
    EXPENSIVE = "expensive"     # Resource-intensive operations
    WRITE = "write"            # State-modifying operations
    READ = "read"              # Read operations (more permissive)
    PUBLIC = "public"          # Public endpoints (least permissive)


# Centralized limits — modify with care
RATE_LIMITS = {
    # ===== AUTH (very strict to prevent brute force) =====
    RateLimitTier.AUTH: {
        "login": "5/minute;20/hour",
        "login_per_ip": "10/minute",
        "refresh": "30/minute",
        "logout": "10/minute",
        "password_reset": "3/hour",
        "mfa_verify": "10/minute",
    },
    
    # ===== EXPENSIVE (compute or storage heavy) =====
    RateLimitTier.EXPENSIVE: {
        "simulation_run": "10/minute;100/hour",
        "simulation_run_per_org": "200/hour",
        "report_generate": "5/minute;50/hour",
        "monte_carlo_large": "5/hour",  # > 50K samples
        "sobol_analysis": "10/minute",
        "cfd_case_run": "5/hour",
        "fleet_analysis": "2/hour",
        "calibration": "5/day",
    },
    
    # ===== WRITE (state-modifying) =====
    RateLimitTier.WRITE: {
        "create": "30/minute",
        "update": "60/minute",
        "delete": "30/minute",
    },
    
    # ===== READ (more permissive) =====
    RateLimitTier.READ: {
        "list": "300/minute",
        "get_by_id": "600/minute",
        "search": "60/minute",
        "export": "10/minute",
    },
    
    # ===== PUBLIC (very strict) =====
    RateLimitTier.PUBLIC: {
        "register": "3/hour",
        "forgot_password": "3/hour",
    },
}


# Request size limits (prevent DoS via large payloads)
REQUEST_SIZE_LIMITS = {
    "default_max_body_size_mb": 1,           # Most endpoints
    "auth_max_body_size_mb": 0.1,            # Login payload is small
    "simulation_create_max_mb": 5,           # Simulation config can be large
    "report_upload_max_mb": 50,             # Report files
    "bulk_operation_max_mb": 10,             # Bulk endpoints
}


# Request timeout limits (prevent slow loris attacks)
REQUEST_TIMEOUTS = {
    "default_seconds": 30,
    "simulation_submit_seconds": 5,        # Should be fast
    "large_query_seconds": 60,              # Big reads allowed
    "report_generate_seconds": 120,         # PDF generation is slow
}
