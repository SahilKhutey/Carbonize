"""Reagent formulation model."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class CalciumSourceType(str, Enum):
    """Types of calcium sources for the biomineralization matrix."""
    LIME = "Ca(OH)2"
    STEEL_SLAG = "steel_slag"
    WASTE_LIME = "waste_lime"
    CEMENT_KILN_DUST = "ckd"


@dataclass(frozen=True)
class ReagentFormulation:
    """Biomimetic capture matrix formulation."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = "Standard Formulation"
    
    # Matrix composition (weight percent)
    chitosan_wt_pct: Decimal = Decimal("3.0")
    ca_source_type: CalciumSourceType = CalciumSourceType.LIME
    ca_wt_pct: Decimal = Decimal("3.5")
    
    # Enzyme
    enzyme_type: str = "bovine_CA"
    enzyme_mg_per_l: Decimal = Decimal("12.0")
    
    # Additives
    additives: list[dict] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        if not 0.5 <= self.chitosan_wt_pct <= 6.0:
            raise ValueError("chitosan_wt_pct must be in [0.5, 6.0]")
        if not 1.0 <= self.ca_wt_pct <= 10.0:
            raise ValueError("ca_wt_pct must be in [1.0, 10.0]")
