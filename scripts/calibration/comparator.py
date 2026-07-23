"""
Compare model predictions against observations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import t as t_dist

from cbms_shared.logging import get_logger
from .fitters import FitResult

logger = get_logger(__name__)


class PredictionComparator:
    """
    Compare a fitted model's predictions against the observations it was
    (or will be) evaluated against.

    Deliberately takes a FitResult, not the reactor-level UQRunner output.
    UQRunner produces a single fixed full-plant scenario's predicted
    capture-efficiency distribution (e.g. "co2_capture_pct": {mean, std}
    for one hardcoded 10,000 Nm3/hr plant) -- that is not the same
    physical quantity as a CE-1 bench measurement (an enzyme reaction rate
    in mol/L/s at specific bench conditions), so it cannot be validly
    compared row-for-row against raw experimental observations. FitResult,
    by contrast, already carries per-observation residuals computed at
    each observation's own actual conditions using the fitted parameters
    -- that IS the right quantity to validate against.

    IMPORTANT LIMITATION: this checks residuals from the SAME dataset the
    parameters were just fit to (that's the only data calibrate.py's
    current pipeline has available at this step). That makes this a
    goodness-of-fit check, not true out-of-sample predictive validation --
    a least-squares fit's own residuals will always look reasonable
    against its own training data by construction. For genuine hardware
    validation ("does the model predict a NEW pilot batch we didn't use
    to calibrate it"), call compare() again later with a FitResult's
    parameters evaluated against a held-out dataset, not the fitting data.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def compare(
        self,
        fit_result: FitResult,
        observations: pd.DataFrame,
        experiment: str,
        confidence_level: float = 0.90,
    ) -> dict:
        self.logger.info(
            "comparing_predictions_vs_observations",
            experiment=experiment,
            n_observations=len(observations),
        )

        residuals = np.asarray(fit_result.residuals, dtype=float)
        n = fit_result.n_observations

        if n == 0 or len(residuals) == 0:
            return {
                "status": "NO_DATA",
                "experiment": experiment,
                "observations_count": 0,
                f"within_{int(confidence_level*100)}pct_ci_pct": None,
            }

        # Guard against exactly the stub-fitter pattern found in
        # _fit_ce3_precipitation / _fit_ce4_multi_gas / _fit_ce5_formulation:
        # a "fit" that returns rmse=0.0 and all-zero residuals regardless of
        # the actual input data is a placeholder, not a real fit. Without
        # this check, such a placeholder would report a perfect, confident
        # "VALIDATED" result every time -- exactly the false-confidence
        # failure mode this function exists to prevent.
        if fit_result.rmse == 0.0 and np.allclose(residuals, 0.0):
            self.logger.warning(
                "stub_fitter_detected",
                experiment=experiment,
                model_name=fit_result.model_name,
            )
            return {
                "status": "FITTER_NOT_IMPLEMENTED",
                "experiment": experiment,
                "observations_count": int(n),
                f"within_{int(confidence_level*100)}pct_ci_pct": None,
                "message": (
                    f"{fit_result.model_name}'s fitter returned zero RMSE "
                    "and all-zero residuals for every observation -- this "
                    "is the signature of a placeholder implementation, not "
                    "a real fit. Refusing to report VALIDATED against "
                    "fabricated residuals."
                ),
            }

        dof = max(int(fit_result.degrees_of_freedom), 1)
        alpha = 1.0 - confidence_level
        # t-multiplier (not a fixed z=1.645) for consistency with the
        # t-distribution already used for parameter_ci elsewhere in this
        # pipeline, and because bench datasets typically have low degrees
        # of freedom where the normal approximation understates interval
        # width.
        t_mult = t_dist.ppf(1.0 - alpha / 2.0, df=dof)
        residual_band = t_mult * fit_result.rmse

        within_band = np.abs(residuals) <= residual_band
        within_pct = 100.0 * float(np.sum(within_band)) / len(residuals)

        mean_residual = float(np.mean(residuals))
        residual_std = float(np.std(residuals))
        # Bias check: a mean residual that's large relative to the residual
        # spread indicates the model is systematically off-center, not just
        # noisy -- a different (and often more actionable) problem than low
        # coverage. E.g. "always predicts 10% low" vs "unpredictably +/-30%".
        bias_ratio = abs(mean_residual) / residual_std if residual_std > 0 else 0.0

        nominal_pct = confidence_level * 100.0
        if fit_result.r_squared < 0:
            # Worse than predicting the mean -- coverage% can look
            # deceptively fine here because a bad fit inflates RMSE, which
            # widens residual_band and can make everything "fit" inside a
            # band that's only wide because the fit is bad. r_squared < 0
            # is a scale-invariant red flag that overrides a passing
            # coverage number.
            status = "NEEDS_RECALIBRATION"
        elif within_pct >= nominal_pct * 0.85 and bias_ratio < 1.0:
            # In-sample coverage doesn't need to hit the nominal rate
            # exactly (this isn't held-out validation -- see class
            # docstring), but should be reasonably close with no strong
            # centering bias.
            status = "VALIDATED"
        elif within_pct >= nominal_pct * 0.6:
            status = "NEEDS_REVIEW"
        else:
            status = "NEEDS_RECALIBRATION"

        return {
            "status": status,
            "experiment": experiment,
            "observations_count": int(n),
            f"within_{int(confidence_level*100)}pct_ci_pct": round(within_pct, 2),
            "mean_residual": round(mean_residual, 6),
            "residual_std": round(residual_std, 6),
            "bias_ratio": round(bias_ratio, 3),
            "r_squared": fit_result.r_squared,
            "rmse": fit_result.rmse,
            "note": (
                "In-sample goodness-of-fit check against the data used to "
                "fit these parameters, not out-of-sample predictive "
                "validation. For real hardware validation, re-run this "
                "against a held-out dataset (e.g. a later pilot-plant "
                "batch) not used in fitting."
            ),
        }
