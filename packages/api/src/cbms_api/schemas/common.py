"""
Shared Pydantic mixins and validators for strict input validation.
"""

from typing import Annotated
import re
from pydantic import Field


# String length limits
ShortStr = Annotated[str, Field(min_length=1, max_length=255)]
MediumStr = Annotated[str, Field(min_length=1, max_length=1000)]
LongStr = Annotated[str, Field(min_length=1, max_length=10000)]


# Numeric ranges
PositiveInt = Annotated[int, Field(gt=0, lt=2**31)]
PositiveFloat = Annotated[float, Field(gt=0)]
Probability = Annotated[float, Field(ge=0, le=1)]
Percentage = Annotated[float, Field(ge=0, le=100)]


# Validation helpers
SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
SAFE_NAME_PATTERN = re.compile(r"^[\w\s.,&\-()]{1,255}$")
SAFE_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9/_.-]{1,512}$")


def validate_safe_id(value: str) -> str:
    """Validate that string is a safe identifier."""
    if not SAFE_ID_PATTERN.match(value):
        raise ValueError("Invalid identifier format")
    return value


def validate_safe_name(value: str) -> str:
    """Validate human-readable name."""
    if not SAFE_NAME_PATTERN.match(value):
        raise ValueError("Name contains invalid characters")
    return value
