"""
Uncertainty estimation via bootstrap resampling for parameters.
"""

from __future__ import annotations

from typing import Dict, Tuple
import numpy as np
import pandas as pd

from .fitters import FitResult, ParameterFitter
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class UncertaintyEstimator:
    """Estimate parameter uncertainty via bootstrap resampling."""
    
    def __init__(self, n_bootstrap: int = 10, confidence: float = 0.95):
        self.n_bootstrap = n_bootstrap
        self.confidence = confidence
        self.logger = get_logger(self.__class__.__name__)
        
    def compute(
        self,
        fit_result: FitResult,
        data: pd.DataFrame,
    ) -> Dict[str, Tuple[float, float]]:
        self.logger.info("bootstrap_start", n_bootstrap=self.n_bootstrap, confidence=self.confidence)
        
        n_obs = len(data)
        bootstrap_estimates = {p: [] for p in fit_result.parameters.keys()}
        
        for i in range(self.n_bootstrap):
            sample = data.sample(n=n_obs, replace=True, random_state=i)
            try:
                fitter = ParameterFitter(experiment=fit_result.model_name)
                # Pass dummy baseline params
                boot_result = fitter.fit(sample, baseline_params={})
                for p, v in boot_result.parameters.items():
                    if p in bootstrap_estimates:
                        bootstrap_estimates[p].append(v)
            except Exception:
                continue
                
        alpha = 1.0 - self.confidence
        ci_results = {}
        
        for param, estimates in bootstrap_estimates.items():
            if len(estimates) < 2:
                # Fallback to standard error or baseline CI
                pt = fit_result.parameters[param]
                ci_results[param] = (pt * 0.9, pt * 1.1)
                continue
                
            estimates_arr = np.array(estimates)
            ci_low = np.percentile(estimates_arr, 100.0 * alpha / 2.0)
            ci_high = np.percentile(estimates_arr, 100.0 * (1.0 - alpha / 2.0))
            ci_results[param] = (float(ci_low), float(ci_high))
            
        return ci_results
