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
    # Verified against every actual backtick-wrapped constant name in
    # RATE_CONSTANTS_PROVENANCE.md -- the previous mapping (k_cat_CA,
    # k_precip_CaCO3, k_henry_SO2, etc.) never matched anything except
    # E_a_inact by coincidence, so this automation silently did nothing
    # for 11 of 12 parameters, including k_cat itself.
    "CE-1": ["k_cat", "K_M_co2", "K_i_hco3", "ca_inactivation", "E_a_inact"],
    "CE-2": [],  # no heavy-metal Freundlich sorption rows exist in the doc yet
    "CE-3": ["k_precip_caco3", "k_precip_caso3", "k_precip_caso4", "KSP_CACO3", "KSP_CASO4", "KSP_CASO3"],
    "CE-4": ["k_so2_abs", "HENRY_SO2", "K_so2_dissociation", "k_no2_abs", "HENRY_NO2", "K_no2_dissociation"],
    "CE-5": ["strength_coeff_chitosan", "pH_coeff_strength"],
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
                    parts[5] = f" {status_icon} ({timestamp}) "
                    line = "|".join(parts)
                    updated = True
            new_lines.append(line)

        if updated:
            self.doc_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            logger.info("provenance_doc_updated", experiment=experiment, status=comparator_status)
        else:
            logger.warning(
                "provenance_doc_no_matching_rows",
                experiment=experiment,
                target_params=target_params,
                note=(
                    "No rows in RATE_CONSTANTS_PROVENANCE.md matched this "
                    "experiment's tracked parameters -- either the doc has "
                    "no rows for this experiment yet, or EXPERIMENT_PARAMETER_MAP "
                    "is out of sync with the doc's actual constant names. "
                    "The doc was NOT updated."
                ),
            )

        return updated
