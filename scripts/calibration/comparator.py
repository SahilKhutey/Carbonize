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

    # Maps each experiment to the raw observation column its fitters predict.
    # CE-4 has no single response column (removal efficiency is derived from
    # inlet_ppm/outlet_ppm) -- resolved specially in _resolve_target_column.
    _TARGET_COLUMNS = {
        "CE-1": "rate_mol_per_L_s",
        "CE-2": "loading_mg_per_g",
        "CE-3": "rate_mol_per_L_s",
        "CE-5": "response",
    }

    def _resolve_target_column(self, experiment: str, observations: pd.DataFrame) -> pd.Series | None:
        """
        Return the observed response values (as a Series) that
        fit_result.residuals were computed against, or None if this
        experiment has no single resolvable response column (currently
        CE-4, whose target -- gas removal efficiency -- is derived from
        inlet_ppm/outlet_ppm rather than being a single raw column; CE-4's
        fitter is a stub as of this writing, so this only matters once a
        real CE-4 fitter exists).
        """
        if experiment == "CE-4":
            if "inlet_ppm" in observations.columns and "outlet_ppm" in observations.columns:
                inlet = observations["inlet_ppm"]
                return ((inlet - observations["outlet_ppm"]) / inlet.replace(0, np.nan)) * 100.0
            return None
        col = self._TARGET_COLUMNS.get(experiment)
        if col is None or col not in observations.columns:
            return None
        return observations[col]

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
                "mape_pct": None,
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
                "mape_pct": None,
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

        # MAPE: only computable if we can resolve which raw observation
        # column these residuals were measured against (see
        # _resolve_target_column). Left as None rather than 0.0 when it
        # can't be resolved -- a fabricated 0.0% error is worse than an
        # honest "not computed" for a number that feeds engineering
        # decisions (e.g. the batch calibration summary report).
        mape_pct = None
        observed = self._resolve_target_column(experiment, observations)
        if observed is not None:
            observed = observed.to_numpy(dtype=float)[: len(residuals)]
            nonzero = observed != 0
            if np.any(nonzero):
                mape_pct = float(
                    np.mean(np.abs(residuals[: len(observed)][nonzero] / observed[nonzero])) * 100.0
                )

        nominal_pct = confidence_level * 100.0
        if fit_result.r_squared < 0.50:
            # Poor fit or worse than predicting the mean -- coverage% can look
            # deceptively fine because a bad fit inflates RMSE, which widens
            # residual_band. Requiring R² >= 0.50 prevents low R² models
            # from reporting false-positive VALIDATED status.
            status = "NEEDS_RECALIBRATION"
        elif fit_result.r_squared >= 0.80 and within_pct >= nominal_pct * 0.85 and bias_ratio < 1.0:
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
            "mape_pct": round(mape_pct, 3) if mape_pct is not None else None,
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
