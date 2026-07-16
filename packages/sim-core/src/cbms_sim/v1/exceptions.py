"""
Public exception hierarchy for sim-core v1 API.

All exceptions inherit from SimulationError. Callers should catch
the most specific exception type they can handle.
"""

from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, field


class ErrorCode(str, Enum):
    """Stable error codes for programmatic handling."""
    
    # Validation errors (4xx-equivalent)
    INVALID_INPUT = "INVALID_INPUT"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INCOMPATIBLE_VERSIONS = "INCOMPATIBLE_VERSIONS"
    
    # Numerical errors (5xx-equivalent)
    SOLVER_DIVERGENCE = "SOLVER_DIVERGENCE"
    SOLVER_TIMEOUT = "SOLVER_TIMEOUT"
    MASS_BALANCE_VIOLATION = "MASS_BALANCE_VIOLATION"
    NUMERICAL_INSTABILITY = "NUMERICAL_INSTABILITY"
    
    # Parameter errors
    PARAMETER_NOT_FOUND = "PARAMETER_NOT_FOUND"
    PARAMETER_OUT_OF_RANGE = "PARAMETER_OUT_OF_RANGE"
    PARAMETER_VERSION_MISMATCH = "PARAMETER_VERSION_MISMATCH"
    
    # Resource errors
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    DISK_FULL = "DISK_FULL"
    TIMEOUT = "TIMEOUT"
    
    # Catch-all
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass(frozen=True)
class ErrorContext:
    """Structured error context for debugging."""
    request_id: Optional[str] = None
    run_id: Optional[str] = None
    parameter_set_version: Optional[str] = None
    code_version: Optional[str] = None
    stage: Optional[str] = None  # "kinetics", "mass_balance", etc.
    extra: dict[str, Any] = field(default_factory=dict)


class SimulationError(Exception):
    """
    Base exception for all sim-core errors.
    
    All v1 API errors inherit from this. Use `code` for programmatic
    handling; use `message` and `context` for debugging.
    """
    
    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or ErrorContext()
        self.cause = cause
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.context.stage:
            parts.append(f"[stage={self.context.stage}]")
        if self.context.run_id:
            parts.append(f"[run_id={self.context.run_id}]")
        return " ".join(parts)
    
    def to_dict(self) -> dict:
        """Serialize for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code.value,
            "message": self.message,
            "context": {
                "request_id": self.context.request_id,
                "run_id": self.context.run_id,
                "stage": self.context.stage,
                "parameter_set_version": self.context.parameter_set_version,
                "code_version": self.context.code_version,
                **self.context.extra,
            },
        }


class ValidationError(SimulationError):
    """Input validation failure (Pydantic-style)."""
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", None) or ErrorContext()
        if field:
            context.extra["field"] = field
        super().__init__(message, code=ErrorCode.INVALID_INPUT, context=context, **kwargs)


class ConvergenceError(SimulationError):
    """ODE solver failed to converge."""
    def __init__(self, message: str, nfev: int = 0, **kwargs):
        context = kwargs.pop("context", None) or ErrorContext()
        context.extra["nfev"] = nfev
        super().__init__(message, code=ErrorCode.SOLVER_DIVERGENCE, context=context, **kwargs)


class NumericalError(SimulationError):
    """Numerical issue (NaN, Inf, overflow)."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code=ErrorCode.NUMERICAL_INSTABILITY, **kwargs)


class ParameterError(SimulationError):
    """Parameter set issue (missing, out of range, version mismatch)."""
    def __init__(self, message: str, parameter: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", None) or ErrorContext()
        if parameter:
            context.extra["parameter"] = parameter
        super().__init__(message, context=context, **kwargs)


class ResourceError(SimulationError):
    """Resource exhaustion (memory, disk, time)."""
    pass
