"""Result models."""

from dataclasses import dataclass, field
from typing import Any
import numpy as np
from uuid import UUID, uuid4


@dataclass(frozen=True)
class KineticsResult:
    """Result of reaction kinetics ODE integration."""
    
    id: UUID = field(default_factory=uuid4)
    final_state: dict[str, float] = field(default_factory=dict)
    time_series: dict[str, np.ndarray] = field(default_factory=dict)
    capture_efficiencies: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    input_hash: str = ""
    computation_time_s: float = 0.0


@dataclass(frozen=True)
class MassBalanceResult:
    """Result of mass balance calculation."""
    
    id: UUID = field(default_factory=uuid4)
    input_streams: dict[str, float] = field(default_factory=dict)
    output_streams: dict[str, float] = field(default_factory=dict)
    capture_rates: dict[str, float] = field(default_factory=dict)
    conservation_error_pct: float = 0.0
    cpcb_so2_compliant: bool = True
    so2_outlet_mg_per_nm3: float = 0.0
    computation_time_s: float = 0.0


@dataclass(frozen=True)
class UQResult:
    """Uncertainty quantification result."""
    
    id: UUID = field(default_factory=uuid4)
    samples: np.ndarray = field(default_factory=lambda: np.array([]))
    statistics: dict[str, dict[str, float]] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    computation_time_s: float = 0.0
    outputs: dict[str, np.ndarray] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationResult:
    """Aggregated final simulation result."""
    
    id: UUID = field(default_factory=uuid4)
    run_id: UUID = field(default_factory=uuid4)
    
    # Point estimates
    co2_capture_pct: float = 0.0
    so2_capture_pct: float = 0.0
    block_strength_mpa: float = 0.0
    npv_10yr_inr: float = 0.0
    payback_months: float = 0.0
    
    # Distributions
    distributions: dict[str, dict[str, float]] = field(default_factory=dict)
    
    # Compliance
    cpcb_compliant: bool = True
    ccts_eligible: bool = True
    
    # Metadata
    parameter_set_version: str = ""
    code_version: str = ""
    input_hash: str = ""
    output_hash: str = ""
    created_at: str = ""
