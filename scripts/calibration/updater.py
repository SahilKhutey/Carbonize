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
