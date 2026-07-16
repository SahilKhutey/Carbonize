"""
Reagent formulation input schemas with strict validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ReagentCreateRequest(BaseModel):
    """Strict input validation for reagent creation."""
    
    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,
        "str_max_length": 1000,
    }
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    chitosan_wt_pct: float = Field(..., ge=0.5, le=6.0)
    ca_source_type: str = Field(default="Ca(OH)2", max_length=50)
    ca_wt_pct: float = Field(..., ge=1.0, le=10.0)
    enzyme_type: str = Field(default="bovine_CA", max_length=50)
    enzyme_mg_per_l: float = Field(..., ge=1.0, le=50.0)
