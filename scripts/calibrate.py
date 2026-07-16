#!/usr/bin/env python3
"""
Calibration pipeline for CBMS-Sim.

Ingests experimental data, fits kinetic parameters, updates the parameter
set, re-runs uncertainty quantification, and generates a calibration report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add script directory to path so calibration package can be imported
sys.path.append(str(Path(__file__).parent))

from calibration.comparator import PredictionComparator
from calibration.fitters import ParameterFitter
from calibration.io import DataIngestor, DataValidationError
from calibration.report import ReportGenerator
from calibration.uncertainty import UncertaintyEstimator
from calibration.updater import ParameterSetUpdater
from calibration.uq_runner import UQRunner
from cbms_shared.logging import configure_logging, get_logger

# Configure standard logger
configure_logging(level="INFO")
logger = get_logger(__name__)

# Supported experiments and their column schemas
EXPERIMENT_SCHEMAS = {
    "CE-1": {
        "name": "Carbonic Anhydrase Kinetics",
        "params": ["k_cat", "K_M_co2", "K_i_hco3", "k_inact", "E_a_inact"],
        "required_columns": ["temperature_C", "pH", "CO2_mM", "rate_mol_per_L_s", "CA_U_per_mL"],
        "optional_columns": ["HCO3_mM", "time_h", "replicate"],
    },
    "CE-2": {
        "name": "Heavy Metal Sorption",
        "params": ["K_F_Pb", "K_F_Cd", "K_F_Hg", "K_F_As", "n_Pb", "n_Cd", "n_Hg", "n_As"],
        "required_columns": ["metal", "pH", "equilibrium_conc_mg_L", "loading_mg_per_g", "chitosan_g_L"],
        "optional_columns": ["temperature_C", "time_h", "replicate"],
    },
    "CE-3": {
        "name": "Chitosan CaCO₃ Precipitation",
        "params": ["k_precip_caco3", "k_precip_caso3", "k_precip_caso4"],
        "required_columns": ["Ca_mM", "HCO3_mM", "pH", "chitosan_pct", "rate_mol_per_L_s"],
        "optional_columns": ["temperature_C", "time_h", "replicate"],
    },
    "CE-4": {
        "name": "Multi-Gas Absorption",
        "params": ["k_so2_abs", "k_no2_abs", "K_i_hco3", "alkalinity_budget"],
        "required_columns": ["timestamp", "gas", "inlet_ppm", "outlet_ppm", "pH", "Ca_mM"],
        "optional_columns": ["temperature_C", "L_per_min", "replicate"],
    },
    "CE-5": {
        "name": "Formulation Sensitivity Screen",
        "params": ["chitosan_wt_pct", "pH_initial"],
        "required_columns": ["chitosan_pct", "pH", "response"],
        "optional_columns": ["replicate"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CBMS-Sim Calibration Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to experimental data CSV",
    )
    parser.add_argument(
        "--experiment",
        type=str,
        choices=list(EXPERIMENT_SCHEMAS.keys()),
        help="Experiment type (auto-detect if not specified)",
    )
    parser.add_argument(
        "--auto-detect",
        action="store_true",
        help="Auto-detect experiment type from CSV columns",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/parameters/v2026.2.json"),
        help="Output parameter set path",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output HTML report path",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("data/parameters/v2026.1.json"),
        help="Baseline parameter set (starting point)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    parser.add_argument(
        "--rerun-uq",
        action="store_true",
        default=True,
        help="Re-run UQ after calibration",
    )
    parser.add_argument(
        "--n-uncertainty-samples",
        type=int,
        default=30,
        help="Number of UQ samples",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info(
        "calibration_started",
        data_path=str(args.data),
        experiment=args.experiment,
        output_path=str(args.output),
    )
    
    # 1. Ingest Data
    ingestor = DataIngestor()
    try:
        df, detected_experiment = ingestor.load_and_validate(
            data_path=args.data,
            experiment=args.experiment or args.auto_detect,
            schemas=EXPERIMENT_SCHEMAS,
        )
    except DataValidationError as e:
        logger.error("data_validation_failed", error=str(e))
        return 1
        
    experiment = args.experiment or detected_experiment
    logger.info("data_loaded", rows=len(df), experiment=experiment)
    
    # 2. Load Baseline Parameters
    if not args.baseline.exists():
        logger.error("baseline_not_found", path=str(args.baseline))
        return 1
        
    with open(args.baseline) as f:
        baseline_params = json.load(f)
        
    # 3. Fit Parameters
    fitter = ParameterFitter(experiment=experiment)
    fit_result = fitter.fit(data=df, baseline_params=baseline_params)
    logger.info("fit_complete", r_squared=fit_result.r_squared)
    
    # 4. Quantify Uncertainty
    uncertainty_estimator = UncertaintyEstimator(n_bootstrap=10)
    confidence_intervals = uncertainty_estimator.compute(fit_result=fit_result, data=df)
    
    # 5. Update Parameter Set
    updater = ParameterSetUpdater()
    new_params = updater.update(
        baseline=baseline_params,
        fit_result=fit_result,
        confidence_intervals=confidence_intervals,
        source_data=str(args.data),
    )
    
    if args.dry_run:
        logger.info("dry_run_no_files_written")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(new_params, f, indent=2)
        logger.info("parameter_set_written", path=str(args.output))
        
    # 6. Re-run UQ
    uq_results = None
    if args.rerun_uq and not args.dry_run:
        uq_runner = UQRunner()
        uq_results = uq_runner.run(parameters=new_params, n_samples=args.n_uncertainty_samples)
        
    # 7. Compare predictions
    comparison = None
    if uq_results is not None:
        comparator = PredictionComparator()
        comparison = comparator.compare(predictions=uq_results, observations=df, experiment=experiment)
        
    # 8. Report
    if args.report:
        report_gen = ReportGenerator()
        report_gen.generate(
            output_path=args.report,
            experiment=experiment,
            fit_result=fit_result,
            uncertainty=confidence_intervals,
            uq_results=uq_results,
            comparison=comparison,
            baseline_params=baseline_params,
            new_params=new_params,
        )
        
    logger.info("calibration_complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
