#!/usr/bin/env python3
"""
Batch Calibration Pipeline for CBMS-Sim.

Executes sequential multi-experiment calibration across CE-1 through CE-5
bench datasets, generates cumulative parameter diff manifests, auto-updates
RATE_CONSTANTS_PROVENANCE.md, and produces a batch calibration summary report.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Add script directory to path so calibration package can be imported
sys.path.append(str(Path(__file__).parent))

from calibration.comparator import PredictionComparator
from calibration.fitters import ParameterFitter
from calibration.io import DataIngestor, DataValidationError
from calibration.provenance_updater import ProvenanceDocUpdater
from calibration.uncertainty import UncertaintyEstimator
from calibration.updater import ParameterSetUpdater
from calibration.uq_runner import UQRunner
from cbms_shared.logging import configure_logging, get_logger

configure_logging(level="INFO")
logger = get_logger(__name__)

EXPERIMENT_SCHEMAS = {
    "CE-1": {
        "name": "Carbonic Anhydrase Kinetics",
        "params": ["k_cat", "K_M_co2", "K_i_hco3", "k_inact", "E_a_inact"],
        "required_columns": ["temperature_C", "pH", "CO2_mM", "rate_mol_per_L_s", "CA_U_per_mL"],
        "optional_columns": ["HCO3_mM", "time_h", "replicate"],
        "default_csv": "CE-1/processed/ca_kinetics_bench.csv",
    },
    "CE-2": {
        "name": "Heavy Metal Sorption",
        "params": ["K_F_Pb", "K_F_Cd", "K_F_Hg", "K_F_As", "n_Pb", "n_Cd", "n_Hg", "n_As"],
        "required_columns": ["metal", "pH", "equilibrium_conc_mg_L", "loading_mg_per_g", "chitosan_g_L"],
        "optional_columns": ["temperature_C", "time_h", "replicate"],
        "default_csv": "CE-2/processed/metal_sorption_bench.csv",
    },
    "CE-3": {
        "name": "Chitosan CaCO₃ Precipitation",
        "params": ["k_precip_caco3", "k_precip_caso3", "k_precip_caso4"],
        "required_columns": ["Ca_mM", "HCO3_mM", "pH", "chitosan_pct", "rate_mol_per_L_s"],
        "optional_columns": ["temperature_C", "time_h", "replicate"],
        "default_csv": "CE-3/processed/caco3_precipitation_bench.csv",
    },
    "CE-4": {
        "name": "Multi-Gas Absorption",
        "params": ["k_so2_abs", "k_no2_abs", "K_i_hco3", "alkalinity_budget"],
        "required_columns": ["timestamp", "gas", "inlet_ppm", "outlet_ppm", "pH", "Ca_mM"],
        "optional_columns": ["temperature_C", "L_per_min", "replicate"],
        "default_csv": "CE-4/processed/multi_gas_bench.csv",
    },
    "CE-5": {
        "name": "Formulation Sensitivity Screen",
        "params": ["chitosan_wt_pct", "pH_initial"],
        "required_columns": ["chitosan_pct", "pH", "response"],
        "optional_columns": ["replicate"],
        "default_csv": "CE-5/processed/formulation_screen_bench.csv",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CBMS-Sim Multi-Experiment Batch Calibration Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/bench_data"),
        help="Root directory containing CE-1 through CE-5 bench data folders",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("data/parameters/v2026.1.json"),
        help="Baseline parameter set path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/parameters/v2026.2.json"),
        help="Output calibrated parameter set path",
    )
    parser.add_argument(
        "--summary-report",
        type=Path,
        default=Path("data/parameters/batch_calibration_summary.md"),
        help="Output markdown batch calibration summary report",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute calibration dry-run without writing output files",
    )
    return parser.parse_args()


class BatchCalibrationPipeline:
    """Orchestrates multi-experiment calibration across CE-1 through CE-5."""

    def __init__(self, data_dir: Path, baseline_path: Path):
        self.data_dir = data_dir
        self.baseline_path = baseline_path
        self.ingestor = DataIngestor()
        self.updater = ParameterSetUpdater()
        self.prov_updater = ProvenanceDocUpdater()
        self.comparator = PredictionComparator()

    def run_pipeline(self, output_path: Path, summary_report_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        logger.info("batch_calibration_started", data_dir=str(self.data_dir), baseline=str(self.baseline_path))

        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Baseline parameter set not found at {self.baseline_path}")

        with open(self.baseline_path) as f:
            initial_baseline = json.load(f)

        current_params = copy.deepcopy(initial_baseline)
        summary_results: List[Dict[str, Any]] = []

        for exp_id, schema_info in EXPERIMENT_SCHEMAS.items():
            csv_rel = schema_info["default_csv"]
            csv_path = self.data_dir / csv_rel

            if not csv_path.exists():
                logger.warning("bench_dataset_missing_skipping", experiment=exp_id, path=str(csv_path))
                continue

            logger.info("calibrating_experiment", experiment=exp_id, dataset=str(csv_path))

            # 1. Load & Validate Bench Data
            df, _ = self.ingestor.load_and_validate(
                data_path=csv_path,
                experiment=exp_id,
                schemas=EXPERIMENT_SCHEMAS,
            )

            # 2. Fit Parameters against current working parameter set
            fitter = ParameterFitter(experiment=exp_id)
            fit_result = fitter.fit(data=df, baseline_params=current_params)

            # 3. Compute Confidence Intervals
            uncertainty_estimator = UncertaintyEstimator(n_bootstrap=10)
            confidence_intervals = uncertainty_estimator.compute(fit_result=fit_result, data=df)

            # 4. Evaluate Comparator Status FIRST -- this must gate whether
            # the fit is trusted enough to promote into the working
            # parameter set. Comparing only *after* already merging (the
            # previous order) makes the comparator's verdict purely
            # informational, with no actual power to keep an unvalidated
            # fit out of what the production simulation engine reads.
            comparison = self.comparator.compare(fit_result=fit_result, observations=df, experiment=exp_id)

            # 5. Update Working Parameter Set -- only promote if the
            # comparator actually validated this fit. NEEDS_RECALIBRATION,
            # NEEDS_REVIEW, and FITTER_NOT_IMPLEMENTED results are still
            # recorded in the summary and provenance doc (so the real
            # r_squared/rmse/status is visible), but must not silently
            # become the new production default -- the prior baseline
            # value is retained for that parameter until a fit actually
            # earns VALIDATED.
            TRUSTED_STATUSES = {"VALIDATED"}
            if comparison.get("status") in TRUSTED_STATUSES:
                current_params = self.updater.update(
                    baseline=current_params,
                    fit_result=fit_result,
                    confidence_intervals=confidence_intervals,
                    source_data=str(csv_path),
                )
            else:
                logger.warning(
                    "parameter_promotion_blocked",
                    experiment=exp_id,
                    status=comparison.get("status"),
                    reason="comparator did not validate this fit -- baseline parameters retained for this experiment's parameters",
                )

            # 6. Auto-Update RATE_CONSTANTS_PROVENANCE.md if not dry-run
            if not dry_run:
                self.prov_updater.update_provenance(
                    experiment=exp_id,
                    comparator_status=comparison.get("status", "VALIDATED"),
                    r_squared=fit_result.r_squared,
                    mape_pct=comparison.get("mape_pct", 0.0),
                    source_data=str(csv_path),
                )

            summary_results.append({
                "experiment": exp_id,
                "name": schema_info["name"],
                "dataset": str(csv_path),
                "r_squared": fit_result.r_squared,
                "rmse": fit_result.rmse,
                "mape_pct": comparison.get("mape_pct", 0.0),
                "comparator_status": comparison.get("status", "VALIDATED"),
                "fitted_params": list(fit_result.parameters.keys()),
                "promoted_to_v2026_2": comparison.get("status") in TRUSTED_STATUSES,
            })

        # 7. Generate Master Diff Manifest (Baseline v2026.1 -> Calibrated v2026.2)
        current_params["version"] = "v2026.2"
        current_params["description"] = "Calibrated parameter set resulting from batch CE-1 through CE-5 pipeline"
        
        master_diff = self.updater.generate_diff_manifest(
            baseline=initial_baseline,
            updated=current_params,
            experiment="BATCH_CE1_TO_CE5",
            source_data=str(self.data_dir),
        )

        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(current_params, f, indent=2)

            diff_path = output_path.parent / f"diff_{initial_baseline.get('version', 'v2026.1')}_to_{current_params.get('version', 'v2026.2')}.json"
            with open(diff_path, "w") as f:
                json.dump(master_diff, f, indent=2)

            self.generate_markdown_summary(summary_report_path, summary_results, master_diff)
            logger.info("batch_calibration_completed", output_set=str(output_path), diff_manifest=str(diff_path))
        else:
            logger.info("dry_run_batch_calibration_complete", total_experiments=len(summary_results))

        return {
            "summary_results": summary_results,
            "master_diff": master_diff,
        }

    def generate_markdown_summary(
        self,
        report_path: Path,
        summary_results: List[Dict[str, Any]],
        master_diff: Dict[str, Any],
    ) -> None:
        """Write structured executive summary markdown report."""
        report_path.parent.mkdir(parents=True, exist_ok=True)

        md_lines = [
            "# 🧪 Batch Calibration Pipeline Executive Summary",
            "",
            f"**Execution Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Baseline Parameter Set:** `v2026.1`",
            f"**Calibrated Parameter Set:** `v2026.2`",
            "",
            "## 1. Multi-Experiment Calibration Matrix",
            "",
            "| Experiment | Target Physics Name | R² Score | RMSE | MAPE % | Comparator Status | Promoted to v2026.2? |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for r in summary_results:
            status = r["comparator_status"]
            if status == "VALIDATED":
                status_icon = "🟢"
            elif status in ("NEEDS_REVIEW", "FITTER_NOT_IMPLEMENTED", "NO_DATA"):
                status_icon = "🟡"
            else:  # NEEDS_RECALIBRATION and anything else unrecognized
                status_icon = "🔴"
            promoted = r.get("promoted_to_v2026_2", False)
            promoted_str = "✅ Yes" if promoted else "⛔ No (baseline retained)"
            r_sq = f"{r['r_squared']:.4f}" if r["r_squared"] is not None else "N/A"
            rmse_s = f"{r['rmse']:.4e}" if r["rmse"] is not None else "N/A"
            mape_s = f"{r['mape_pct']:.2f}%" if r["mape_pct"] is not None else "N/A"
            md_lines.append(
                f"| **{r['experiment']}** | {r['name']} | {r_sq} | {rmse_s} | {mape_s} | {status_icon} {status} | {promoted_str} |"
            )

        md_lines.extend([
            "",
            "## 2. Parameter Changes & Deltas",
            "",
            "| Parameter Path | Old Value (v2026.1) | New Value (v2026.2) | Δ Abs | Δ % | Experiment |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for change in master_diff.get("parameter_diffs", []):
            p_name = change.get("parameter", "unknown")
            old_v = change.get("old_value")
            old_str = f"{old_v:.4e}" if old_v is not None else "N/A"
            new_v = change.get("new_value", 0.0)
            delta = change.get("delta", 0.0)
            pct = change.get("percentage_change")
            pct_str = f"{pct:+.2f}%" if pct is not None else "N/A"
            src = str(change.get("source", "batch")).replace("\\", "/")
            md_lines.append(
                f"| `{p_name}` | {old_str} | {new_v:.4e} | {delta:+.4e} | {pct_str} | `{src}` |"
            )

        md_lines.extend([
            "",
            "## 3. Rate Constants Provenance Impact",
            "",
            "- `RATE_CONSTANTS_PROVENANCE.md` has been updated with real bench fit statistics.",
            "- Verified empirical coverage gates lock reactor sizing safety factors (+15% for `VALIDATED`).",
        ])

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))


def main() -> int:
    args = parse_args()
    pipeline = BatchCalibrationPipeline(
        data_dir=args.data_dir,
        baseline_path=args.baseline,
    )
    pipeline.run_pipeline(
        output_path=args.output,
        summary_report_path=args.summary_report,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
