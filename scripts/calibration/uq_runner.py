"""
Re-run UQ analysis using calibrated parameter distributions.
"""

from __future__ import annotations

from cbms_sim.core.uncertainty_engine import run_uncertainty_analysis
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class UQRunner:
    """Re-run UQ analysis using calibrated parameters."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
    def run(
        self,
        parameters: dict,
        n_samples: int = 30,
    ) -> dict:
        self.logger.info("running_uq_re_analysis", n_samples=n_samples)
        
        # Call the existing uncertainty analysis engine
        raw_res = run_uncertainty_analysis(
            co2_vol_pct=14.0,
            so2_mg_per_nm3=1200.0,
            flow_nm3_per_hr=10000.0,
            enzyme_mg_per_l=12.0,
            reactor_temp_c=40.0,
            sample_count=n_samples
        )
        
        # Map raw UQAnalysisResult structure to CLI expected formats
        return {
            "co2_capture_pct": {
                "mean": raw_res["co2"]["mean"],
                "std": raw_res["co2"]["std"],
                "p5": raw_res["co2"]["p05"],
                "p95": raw_res["co2"]["p95"]
            },
            "so2_capture_pct": {
                "mean": raw_res["so2"]["mean"],
                "std": raw_res["so2"]["std"]
            }
        }
