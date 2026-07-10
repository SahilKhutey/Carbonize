"""Common type aliases."""

from typing import NewType
from uuid import UUID

# ID types
OrganizationId = NewType("OrganizationId", UUID)
UserId = NewType("UserId", UUID)
PlantId = NewType("PlantId", UUID)
ReagentId = NewType("ReagentId", UUID)
SimulationRunId = NewType("SimulationRunId", UUID)
ReportId = NewType("ReportId", UUID)

# Numeric types
CaptureEfficiency = NewType("CaptureEfficiency", float)  # Always in percent (0-100)
Concentration = NewType("Concentration", float)  # mol/m³
MassFlow = NewType("MassFlow", float)  # kg/hr
Temperature = NewType("Temperature", float)  # Celsius
Pressure = NewType("Pressure", float)  # bar
