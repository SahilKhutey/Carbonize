"""
Update parameter set JSON file with calibrated values.
"""

from __future__ import annotations

import copy
from datetime import datetime, UTC
from typing import Dict
import numpy as np

from .fitters import FitResult
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class ParameterSetUpdater:
    """Update the parameter set JSON with calibrated values."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
    def update(
        self,
        baseline: dict,
        fit_result: FitResult,
        confidence_intervals: Dict,
        source_data: str,
    ) -> dict:
        self.logger.info("updating_parameter_set", n_params=len(fit_result.parameters))
        
        new_params = copy.deepcopy(baseline)
        
        # Bump version
        old_version = new_params.get("version", "v2026.1")
        try:
            parts = old_version.lstrip('v').split('.')
            if len(parts) >= 2:
                parts[1] = str(int(parts[1]) + 1)
                new_version = "v" + ".".join(parts)
            else:
                new_version = old_version + ".1"
        except Exception:
            new_version = old_version + ".calibrated"
            
        new_params["version"] = new_version
        new_params["last_calibrated"] = datetime.now(UTC).isoformat() + "Z"
        new_params["calibration_source"] = source_data
        
        if "parameters" not in new_params:
            new_params["parameters"] = {}
            
        for path, value in fit_result.parameters.items():
            if path not in new_params["parameters"]:
                new_params["parameters"][path] = {}
                
            param_entry = new_params["parameters"][path]
            param_entry["value"] = float(value)
            param_entry["source_type"] = "measured"
            param_entry["confidence"] = "HIGH"
            param_entry["source"] = f"Calibration from {source_data}"
            
            # Update distribution parameters if normal
            if param_entry.get("distribution") == "normal":
                ci = confidence_intervals.get(path, (value * 0.9, value * 1.1))
                if ci and not np.isnan(ci[0]) and not np.isnan(ci[1]):
                    # Estimate sigma from 95% CI (width is approx 3.92 * sigma)
                    sigma = max((ci[1] - ci[0]) / 3.92, 1e-6)
                    param_entry["dist_params"] = {
                        "mu": float(value),
                        "sigma": float(sigma)
                    }
                    
        if "calibration_history" not in new_params:
            new_params["calibration_history"] = []
            
        new_params["calibration_history"].append({
            "version": new_version,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "source_data": source_data,
            "parameters_updated": list(fit_result.parameters.keys()),
            "fit_quality": fit_result.fit_quality,
            "r_squared": fit_result.r_squared,
            "rmse": fit_result.rmse,
        })
        
        return new_params

    def generate_diff_manifest(
        self,
        baseline: dict,
        updated: dict,
        experiment: str,
        source_data: str,
    ) -> dict:
        """Generate structured before-and-after diff manifest of calibrated parameters."""
        diffs = []
        old_params = baseline.get("parameters", {})
        new_params = updated.get("parameters", {})
        src_norm = str(source_data).replace("\\", "/")
        
        for p_key, new_entry in new_params.items():
            new_val = float(new_entry.get("value", 0.0))
            if p_key in old_params:
                old_val = float(old_params[p_key].get("value", 0.0))
                if abs(old_val - new_val) > 1e-9:
                    delta = new_val - old_val
                    pct_change = (delta / old_val * 100.0) if abs(old_val) > 1e-9 else 0.0
                    diffs.append({
                        "change_type": "UPDATED",
                        "parameter": p_key,
                        "old_value": round(old_val, 6),
                        "new_value": round(new_val, 6),
                        "delta": round(delta, 6),
                        "percentage_change": round(pct_change, 2),
                        "old_confidence": old_params[p_key].get("confidence", "UNKNOWN"),
                        "new_confidence": new_entry.get("confidence", "HIGH"),
                        "source": src_norm,
                    })
            else:
                diffs.append({
                    "change_type": "NEW_CALIBRATED_PARAMETER",
                    "parameter": p_key,
                    "old_value": None,
                    "new_value": round(new_val, 6),
                    "delta": round(new_val, 6),
                    "percentage_change": None,
                    "old_confidence": "UNSET",
                    "new_confidence": new_entry.get("confidence", "HIGH"),
                    "source": src_norm,
                })
                    
        return {
            "experiment": experiment,
            "from_version": baseline.get("version", "v2026.1"),
            "to_version": updated.get("version", "v2026.2"),
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "source_data": src_norm,
            "changes_count": len(diffs),
            "parameter_diffs": diffs,
        }

