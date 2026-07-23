import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parents[3] / "scripts"))

import pytest
import pandas as pd
import numpy as np
from calibration.comparator import PredictionComparator
from calibration.fitters import FitResult


def test_prediction_comparator_validated():
    comparator = PredictionComparator()

    df_obs = pd.DataFrame({
        "rate_mol_per_L_s": [82.0, 84.0, 86.0, 85.0, 83.0]
    })

    fit_res = FitResult(
        parameters={"kinetics.k_cat": 1.0e6},
        parameter_stderr={"kinetics.k_cat": 0.05e6},
        parameter_ci={"kinetics.k_cat": (0.9e6, 1.1e6)},
        covariance=np.eye(1),
        r_squared=0.95,
        rmse=1.0,
        mae=0.8,
        aic=10.0,
        bic=11.0,
        residuals=np.array([-0.5, 0.2, -0.3, 0.4, 0.1]),
        n_observations=5,
        n_parameters=1,
        degrees_of_freedom=4,
        fit_quality="GOOD",
        model_name="CE-1 CA Kinetics",
        convergence=True,
    )

    res = comparator.compare(fit_result=fit_res, observations=df_obs, experiment="CE-1")

    assert res["status"] == "VALIDATED"
    assert res["within_90pct_ci_pct"] == 100.0
    assert res["observations_count"] == 5


def test_prediction_comparator_stub_fitter():
    comparator = PredictionComparator()

    df_obs = pd.DataFrame({
        "outlet_ppm": [250.0, 300.0, 280.0, 310.0]
    })

    stub_fit_res = FitResult(
        parameters={},
        parameter_stderr={},
        parameter_ci={},
        covariance=np.empty((0, 0)),
        r_squared=0.0,
        rmse=0.0,
        mae=0.0,
        aic=0.0,
        bic=0.0,
        residuals=np.zeros(4),
        n_observations=4,
        n_parameters=0,
        degrees_of_freedom=4,
        fit_quality="STUB",
        model_name="CE-4 Multi-gas Stub",
        convergence=False,
    )

    res = comparator.compare(fit_result=stub_fit_res, observations=df_obs, experiment="CE-4")

    assert res["status"] == "FITTER_NOT_IMPLEMENTED"
    assert res["within_90pct_ci_pct"] is None
    assert "placeholder" in res["message"].lower()
