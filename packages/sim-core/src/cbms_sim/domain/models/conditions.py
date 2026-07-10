"""Operating conditions model."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class OperatingConditions:
    """Reactor operating conditions."""
    
    reactor_temp_c: Decimal = Decimal("40.0")
    pH_initial: Decimal = Decimal("8.5")
    liquid_to_gas_ratio: Decimal = Decimal("8.5")
    residence_time_s: Decimal = Decimal("27.0")
    mesh_count: int = 6
    press_force_bar: Decimal = Decimal("200.0")
    curing_temperature_c: Decimal = Decimal("25.0")
    curing_time_h: Decimal = Decimal("48.0")
    
    def __post_init__(self) -> None:
        if not 20.0 <= self.reactor_temp_c <= 80.0:
            raise ValueError("reactor_temp_c must be in [20, 80]")
        if not 3.0 <= self.liquid_to_gas_ratio <= 20.0:
            raise ValueError("L/G ratio must be in [3, 20]")
        if not 50.0 <= self.press_force_bar <= 500.0:
            raise ValueError("press_force_bar must be in [50, 500]")
