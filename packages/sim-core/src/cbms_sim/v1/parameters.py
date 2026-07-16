"""
Parameter registry for v1 API.

Provides stable access to the parameter set with versioning.
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from cbms_sim.v1.types import ParameterSet
from cbms_sim.v1.exceptions import ParameterError


class ParameterRegistry:
    """
    Access to versioned parameter sets.
    
    Usage:
        registry = ParameterRegistry.from_version("v2026.1")
        k_cat = registry.get("kinetics.k_cat")  # value, source, units, etc.
    """
    
    def __init__(self, parameter_set: ParameterSet):
        self._set = parameter_set
    
    @property
    def version(self) -> str:
        return str(self._set.version)
    
    @property
    def description(self) -> str:
        return self._set.description
    
    @property
    def created_at(self) -> datetime:
        return self._set.created_at
    
    @property
    def parameters(self) -> dict:
        """All parameters as nested dict."""
        return self._set.parameters
    
    def get(self, path: str) -> dict:
        """
        Get parameter by dot-notation path.
        
        Args:
            path: e.g., "kinetics.k_cat"
        
        Returns:
            Dict with keys: value, units, source, source_type, etc.
        
        Raises:
            ParameterError: If path not found
        """
        try:
            return self._set.get_parameter(path)
        except KeyError as e:
            raise ParameterError(
                f"Parameter '{path}' not found in set {self.version}",
                parameter=path,
            ) from e
    
    def get_value(self, path: str) -> float:
        """Get just the value (raises ParameterError if not found)."""
        return float(self.get(path)["value"])
    
    def list_parameters(self, prefix: str = "") -> list[str]:
        """List all parameter paths, optionally filtered by prefix."""
        all_paths = self._flatten(self._set.parameters, "")
        if prefix:
            return [p for p in all_paths if p.startswith(prefix)]
        return all_paths
    
    def _flatten(self, d: dict, prefix: str) -> list[str]:
        """Recursively flatten nested dict to list of dot-paths."""
        result = []
        for key, value in d.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict) and "value" not in value:
                result.extend(self._flatten(value, path))
            else:
                result.append(path)
        return result
    
    @classmethod
    def from_file(cls, path: Path | str) -> "ParameterRegistry":
        """Load parameter set from a file path."""
        try:
            path = Path(path)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            raw_params = data.get("parameters", {})
            nested_params = {}
            for k, v in raw_params.items():
                parts = k.split(".")
                d = nested_params
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                d[parts[-1]] = v
            
            version = data.get("version", "1.0.0")
            if not version.startswith("v") and not version.lstrip('v').replace('.', '').isdigit():
                version = "v" + version
            
            created_at_str = data.get("created_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            else:
                created_at = datetime.now(timezone.utc)
                
            parameter_set = ParameterSet(
                version=version,
                description=data.get("description", ""),
                created_at=created_at,
                parameters=nested_params,
                calibration_history=data.get("calibration_history", [])
            )
            return cls(parameter_set)
        except Exception as e:
            raise ParameterError(f"Failed to load parameter file {path}: {e}") from e
    
    @classmethod
    def from_version(cls, version: str, cache_dir: Optional[str] = None) -> "ParameterRegistry":
        """Load parameter set by version string."""
        version_clean = version.lstrip("v")
        paths = [
            Path(f"data/parameters/{version}.json"),
            Path(f"data/parameters/v{version}.json"),
            Path(f"data/parameters/{version_clean}.json"),
            Path(f"data/parameters/v{version_clean}.json"),
            Path(f"packages/sim-core/data/parameters/{version}.json"),
        ]
        
        # Try to resolve paths relative to current directory or workspace root
        for p in paths:
            if p.exists():
                return cls.from_file(p)
            resolved_p = Path("c:/Users/ASUS/Documents/Carbonize") / p
            if resolved_p.exists():
                return cls.from_file(resolved_p)
                
        raise ParameterError(f"Parameter set '{version}' not found", parameter=version)
