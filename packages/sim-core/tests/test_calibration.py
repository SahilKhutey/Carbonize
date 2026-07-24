import sys
from pathlib import Path
import pytest
import pandas as pd

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.append(str(scripts_dir))

from calibration.io import DataIngestor
from calibration.fitters import ParameterFitter
from calibration.updater import ParameterSetUpdater


def test_calibration_io():
    csv_path = Path(__file__).parent.parent.parent.parent / "data/bench_data/CE-1/processed/ca_rates.csv"
    assert csv_path.exists()
    
    ingestor = DataIngestor()
    df, experiment = ingestor.load_and_validate(csv_path, experiment="CE-1")
    
    assert experiment == "CE-1"
    assert len(df) == 10
    assert "temperature_C" in df.columns


def test_parameter_fitting():
    csv_path = Path(__file__).parent.parent.parent.parent / "data/bench_data/CE-1/processed/ca_rates.csv"
    ingestor = DataIngestor()
    df, _ = ingestor.load_and_validate(csv_path, experiment="CE-1")
    
    fitter = ParameterFitter(experiment="CE-1")
    baseline = {
        "parameters": {
            "kinetics.k_cat": {"value": 1.0e6},
            "kinetics.K_M_co2": {"value": 8.5},
            "kinetics.K_i_hco3": {"value": 26.0},
            # kJ/mol, matching data/parameters/v2026.1.json's declared
            # "unit": "kJ/mol" for this parameter -- NOT J/mol. The fitter
            # converts this to J/mol internally (see fitters.py).
            "kinetics.E_a_inact": {"value": 85.0}
        }
    }
    
    fit_result = fitter.fit(df, baseline)
    assert fit_result.r_squared is not None
    assert "kinetics.k_cat" in fit_result.parameters
    assert fit_result.parameters["kinetics.k_cat"] > 0


def test_parameter_updater():
    baseline = {
        "version": "v2026.1",
        "parameters": {
            "kinetics.k_cat": {
                "value": 1.0e6,
                "distribution": "normal"
            }
        }
    }
    
    class DummyFitResult:
        parameters = {"kinetics.k_cat": 1.5e6}
        r_squared = 0.98
        rmse = 0.01
        fit_quality = "GOOD"
        
    fit_result = DummyFitResult()
    cis = {"kinetics.k_cat": (1.4e6, 1.6e6)}
    
    updater = ParameterSetUpdater()
    updated = updater.update(baseline, fit_result, cis, "test_source.csv")
    
    assert updated["version"] == "v2026.2"
    assert updated["parameters"]["kinetics.k_cat"]["value"] == 1.5e6
    assert updated["parameters"]["kinetics.k_cat"]["confidence"] == "HIGH"


def test_ce3_parameter_fitting():
    csv_path = Path(__file__).parent.parent.parent.parent / "data/bench_data/CE-3/processed/caco3_precipitation_bench.csv"
    assert csv_path.exists()
    ingestor = DataIngestor()
    df, _ = ingestor.load_and_validate(csv_path, experiment="CE-3")
    
    fitter = ParameterFitter(experiment="CE-3")
    baseline = {
        "parameters": {
            "kinetics.k_precip_caco3": {"value": 1.5e-2}
        }
    }
    
    fit_result = fitter.fit(df, baseline)
    assert fit_result.model_name == "CE-3"
    assert "kinetics.k_precip_caco3" in fit_result.parameters
    assert fit_result.parameters["kinetics.k_precip_caco3"] > 0
    assert fit_result.rmse > 0
    assert fit_result.r_squared is not None
    assert len(fit_result.residuals) == len(df)
    assert fit_result.convergence is True


def test_ce4_parameter_fitting():
    csv_path = Path(__file__).parent.parent.parent.parent / "data/bench_data/CE-4/processed/multi_gas_bench.csv"
    assert csv_path.exists()
    ingestor = DataIngestor()
    df, _ = ingestor.load_and_validate(csv_path, experiment="CE-4")
    
    fitter = ParameterFitter(experiment="CE-4")
    baseline = {
        "parameters": {
            "kinetics.k_so2_abs": {"value": 2.5e-2},
            "kinetics.k_no2_abs": {"value": 1.0e-2},
        }
    }
    
    fit_result = fitter.fit(df, baseline)
    assert fit_result.model_name == "CE-4"
    assert "kinetics.k_so2_abs" in fit_result.parameters
    assert "kinetics.k_no2_abs" in fit_result.parameters
    assert fit_result.parameters["kinetics.k_so2_abs"] > 0
    assert fit_result.parameters["kinetics.k_no2_abs"] > 0
    assert fit_result.rmse > 0
    assert fit_result.r_squared is not None
    assert len(fit_result.residuals) == len(df)
    assert fit_result.convergence is True


def test_ce5_parameter_fitting():
    csv_path = Path(__file__).parent.parent.parent.parent / "data/bench_data/CE-5/processed/formulation_screen_bench.csv"
    assert csv_path.exists()
    ingestor = DataIngestor()
    df, _ = ingestor.load_and_validate(csv_path, experiment="CE-5")
    
    fitter = ParameterFitter(experiment="CE-5")
    baseline = {
        "parameters": {
            "kinetics.strength_coeff_chitosan": {"value": 2.5},
            "kinetics.pH_coeff_strength": {"value": 0.1},
        }
    }
    
    fit_result = fitter.fit(df, baseline)
    assert fit_result.model_name == "CE-5"
    assert "kinetics.strength_coeff_chitosan" in fit_result.parameters
    assert "kinetics.pH_coeff_strength" in fit_result.parameters
    assert fit_result.parameters["kinetics.strength_coeff_chitosan"] > 0
    assert fit_result.rmse > 0
    assert fit_result.r_squared is not None
    assert len(fit_result.residuals) == len(df)
    assert fit_result.convergence is True



