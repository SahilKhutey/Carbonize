"""
Automatic Rate Constants Provenance Updater.

Updates packages/sim-core/src/cbms_sim/domain/parameters/RATE_CONSTANTS_PROVENANCE.md
based on empirical calibration and PredictionComparator status gates.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
from cbms_shared.logging import get_logger

logger = get_logger(__name__)

PROVENANCE_FILE_PATH = Path("packages/sim-core/src/cbms_sim/domain/parameters/RATE_CONSTANTS_PROVENANCE.md")

EXPERIMENT_PARAMETER_MAP = {
    "CE-1": ["k_cat_CA", "E_a_inact"],
    "CE-2": ["K_F_Pb", "n_Pb", "K_F_Cd", "n_Cd"],
    "CE-3": ["k_precip_CaCO3", "K_sp_CaCO3"],
    "CE-4": ["k_henry_SO2", "k_henry_NOx"],
    "CE-5": ["strength_coeff_chitosan", "curing_temp_mod"],
}


class ProvenanceDocUpdater:
    """Updates the RATE_CONSTANTS_PROVENANCE.md table based on empirical comparison results."""

    def __init__(self, doc_path: Path = PROVENANCE_FILE_PATH):
        self.doc_path = doc_path

    def update_provenance(
        self,
        experiment: str,
        comparator_status: str,
        r_squared: float,
        mape_pct: float,
        source_data: str,
    ) -> bool:
        """Update status icons and calibration metrics in RATE_CONSTANTS_PROVENANCE.md."""
        if not self.doc_path.exists():
            logger.warning("provenance_doc_not_found", path=str(self.doc_path))
            return False

        content = self.doc_path.read_text(encoding="utf-8")
        
        # Determine status icon
        if comparator_status == "VALIDATED":
            status_icon = "🟢 Bench-Validated"
        elif comparator_status in ("NEEDS_RECALIBRATION", "OVERCONFIDENT_UQ"):
            status_icon = "🟡 Needs Recalibration"
        else:
            status_icon = "🔴 Discrepant / High Risk"

        timestamp = datetime.now(UTC).strftime("%Y-%m-%d")
        lines = content.splitlines()
        new_lines = []
        updated = False
        target_params = EXPERIMENT_PARAMETER_MAP.get(experiment, [])

        for line in lines:
            # Check if line matches experiment parameter or experiment tag
            match_param = any(p in line for p in target_params)
            if (experiment in line or match_param) and "|" in line and not line.startswith("| Parameter"):
                parts = line.split("|")
                if len(parts) >= 6:
                    if comparator_status == "VALIDATED":
                        parts[5] = f" 🟢 {status_icon} ({timestamp}) "
                    elif "NEEDS_RECALIBRATION" in comparator_status:
                        parts[5] = f" 🟡 {status_icon} ({timestamp}) "
                    else:
                        parts[5] = f" 🔴 {status_icon} ({timestamp}) "
                    line = "|".join(parts)
                    updated = True
            new_lines.append(line)

        if updated:
            self.doc_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            logger.info("provenance_doc_updated", experiment=experiment, status=comparator_status)
        
        return updated
