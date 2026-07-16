"""Parameter registry model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ParameterRegistry:
    """Registry for physical, chemical, and economic parameters."""
    
    def __init__(self, version: str, parameters: dict[str, Any]) -> None:
        self.version = version
        self.parameters = parameters
        
    @classmethod
    def from_file(cls, path: Path | str) -> ParameterRegistry:
        """Load registry from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            version=data.get("version", ""),
            parameters=data.get("parameters", {}),
        )
        
    def get(self, key: str) -> dict[str, Any]:
        """Get parameter dict by key."""
        if key not in self.parameters:
            raise KeyError(f"Parameter '{key}' not found in registry")
        return self.parameters[key]
        
    def get_value(self, key: str) -> float:
        """Get parameter value by key."""
        return float(self.get(key)["value"])
