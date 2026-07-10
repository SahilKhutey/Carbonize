"""Exception hierarchy for the CBMS platform."""

from typing import Any


class CBMSError(Exception):
    """Base exception for all CBMS errors."""
    
    def __init__(self, message: str, *, code: str | None = None, **context: Any):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.context = context
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }


class ScientificError(CBMSError):
    """Errors in scientific computation."""
    pass


class NumericalDivergenceError(ScientificError):
    """ODE solver failed to converge."""
    pass


class InvalidParameterError(ScientificError):
    """Parameter outside valid range."""
    pass


class InsufficientSolidError(ScientificError):
    """Solid product below threshold."""
    pass


class UQConvergenceError(ScientificError):
    """Monte Carlo or Sobol failed to converge."""
    pass


class DataError(CBMSError):
    """Errors in data layer."""
    pass


class NotFoundError(DataError):
    """Entity not found."""
    pass


class ValidationFailedError(DataError):
    """Input validation failed."""
    pass


class IntegrityError(DataError):
    """Database integrity constraint violated."""
    pass


class InfrastructureError(CBMSError):
    """Errors in infrastructure."""
    pass


class ExternalServiceError(InfrastructureError):
    """External service unavailable."""
    pass


class TimeoutError(InfrastructureError):
    pass


class APIError(CBMSError):
    """Errors in API layer."""
    pass


class AuthenticationError(APIError):
    pass


class AuthorizationError(APIError):
    pass


class RateLimitError(APIError):
    pass
