"""
tests/test_ml.py  (extended version)
Tests for KineticsSurrogateModel — 5-output GP with feature scaling.
"""

import numpy as np
import pytest
from cbms_sim.ml.surrogate_model import KineticsSurrogateModel, OUTPUT_NAMES, FEATURE_NAMES


@pytest.fixture(scope="module")
def fitted_model():
    """Fit once per module — ODE calls are the expensive part."""
    model = KineticsSurrogateModel()
    model.fit(samples=20)   # small for fast CI; increase for production accuracy
    return model


class TestSurrogateModelStructure:
    def test_has_correct_number_of_gps(self):
        model = KineticsSurrogateModel()
        assert len(model.gps) == len(OUTPUT_NAMES) == 5

    def test_not_fitted_raises(self):
        model = KineticsSurrogateModel()
        with pytest.raises(RuntimeError, match="fitted"):
            model.predict_capture(enzyme=12.0, temp=40.0, flow=10000.0)

    def test_fit_marks_fitted(self, fitted_model):
        assert fitted_model.fitted is True

    def test_feature_names(self):
        assert FEATURE_NAMES == ["enzyme_mg_per_l", "reactor_temp_c", "flow_nm3_per_hr"]

    def test_output_names(self):
        assert set(OUTPUT_NAMES) == {"co2_pct", "so2_pct", "nox_pct", "pm_pct", "metal_pct"}


class TestPredictions:
    def test_all_keys_present(self, fitted_model):
        result = fitted_model.predict_capture(enzyme=12.0, temp=40.0, flow=10000.0)
        for name in OUTPUT_NAMES:
            assert f"{name}_capture_pct"        in result
            assert f"{name}_uncertainty_1sigma" in result

    def test_backwards_compat_keys(self, fitted_model):
        result = fitted_model.predict_capture(enzyme=12.0, temp=40.0, flow=10000.0)
        assert "co2_capture_efficiency_pct" in result
        assert "co2_uncertainty_pct"        in result
        assert "so2_capture_efficiency_pct" in result
        assert "so2_uncertainty_pct"        in result

    def test_predictions_bounded(self, fitted_model):
        result = fitted_model.predict_capture(enzyme=25.0, temp=35.0, flow=5000.0)
        for name in OUTPUT_NAMES:
            pct = result[f"{name}_capture_pct"]
            assert 0.0 <= pct <= 100.0, f"{name} out of range: {pct}"

    def test_uncertainty_non_negative(self, fitted_model):
        result = fitted_model.predict_capture(enzyme=12.0, temp=40.0, flow=10000.0)
        for name in OUTPUT_NAMES:
            sigma = result[f"{name}_uncertainty_1sigma"]
            assert sigma >= 0.0, f"{name} sigma negative: {sigma}"

    def test_different_inputs_give_different_predictions(self, fitted_model):
        low  = fitted_model.predict_capture(enzyme=1.0,  temp=20.0, flow=1000.0)
        high = fitted_model.predict_capture(enzyme=50.0, temp=60.0, flow=15000.0)
        # At least one output should differ
        diffs = [
            abs(low[f"{n}_capture_pct"] - high[f"{n}_capture_pct"])
            for n in OUTPUT_NAMES
        ]
        assert max(diffs) > 0.01


class TestOnlineRefinement:
    def test_add_training_point_increases_dataset(self, fitted_model):
        n_before = len(fitted_model._X_train)
        fitted_model.add_training_point(
            enzyme=20.0, temp=38.0, flow=8000.0,
            captures={"co2_pct": 97.0, "so2_pct": 15.0, "nox_pct": 62.0,
                      "pm_pct": 89.0, "metal_pct": 95.0}
        )
        assert len(fitted_model._X_train) == n_before + 1
        assert fitted_model.fitted is True

    def test_add_point_still_predicts(self, fitted_model):
        result = fitted_model.predict_capture(enzyme=20.0, temp=38.0, flow=8000.0)
        assert "co2_pct_capture_pct" in result


class TestNoConvergenceWarning:
    """Verify GP training does not emit ConvergenceWarning (length scale bounds issue)."""

    def test_no_convergence_warning(self, recwarn):
        import warnings
        from sklearn.exceptions import ConvergenceWarning
        model = KineticsSurrogateModel()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            model.fit(samples=15)
        conv_warnings = [x for x in w if issubclass(x.category, ConvergenceWarning)]
        assert len(conv_warnings) == 0, (
            f"Got {len(conv_warnings)} ConvergenceWarning(s). "
            "Widen ARD length_scale_bounds in _make_kernel()."
        )
