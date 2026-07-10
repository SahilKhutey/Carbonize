"""Plant profile model."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PlantProfile:
    """Industrial plant emission profile."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    location: str = ""
    boiler_type: str = "pulverized_coal"
    
    # Flue gas parameters
    exhaust_flow_nm3_hr: Decimal = Decimal("10000.0")
    baseline_temperature_c: Decimal = Decimal("150.0")
    
    # Pollutant concentrations
    co2_vol_pct: Decimal = Decimal("14.0")
    so2_mg_per_nm3: Decimal = Decimal("1200.0")
    nox_mg_per_nm3: Decimal = Decimal("500.0")
    fly_ash_g_per_nm3: Decimal = Decimal("45.0")
    heavy_metal_profile: list[dict] = field(default_factory=list)
    
    # Operating
    operating_hours_per_year: int = 8000
    
    def __post_init__(self) -> None:
        if self.exhaust_flow_nm3_hr <= 0:
            raise ValueError("exhaust_flow_nm3_hr must be > 0")
        if not 0 <= self.co2_vol_pct <= 100:
            raise ValueError("co2_vol_pct must be in [0, 100]")
