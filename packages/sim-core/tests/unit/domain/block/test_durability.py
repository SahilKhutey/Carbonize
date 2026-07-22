"""
tests/unit/domain/block/test_durability.py
Unit tests for BlockDurabilityModel.
"""

import pytest
from cbms_sim.domain.block.durability import BlockDurabilityModel, DurabilityResult


@pytest.fixture
def model():
    return BlockDurabilityModel()


class TestFreezThaw:
    def test_high_strength_gives_low_risk(self, model):
        """Strong blocks (M35+) should have ≥100 freeze-thaw cycles (medium or low risk)."""
        result = model.predict(compressive_strength_mpa=35.0, water_cement_ratio=0.35)
        assert result.freeze_thaw_cycles_to_failure >= 100
        assert result.freeze_thaw_risk in ("low", "medium")

    def test_low_strength_gives_high_risk(self, model):
        """Weak blocks should have fewer freeze-thaw cycles."""
        high = model.predict(compressive_strength_mpa=30.0)
        low  = model.predict(compressive_strength_mpa=5.0)
        assert high.freeze_thaw_cycles_to_failure > low.freeze_thaw_cycles_to_failure

    def test_freeze_thaw_index_bounded(self, model):
        for strength in [5.0, 15.0, 25.0, 40.0]:
            r = model.predict(compressive_strength_mpa=strength)
            assert 0.0 <= r.freeze_thaw_index <= 1.0


class TestLeach:
    def test_cpcb_compliance_at_low_gypsum(self, model):
        """Low gypsum fraction + high metal capture → CPCB compliant."""
        result = model.predict(
            compressive_strength_mpa=25.0,
            gypsum_fraction=0.02,
            heavy_metal_capture_pct=98.0,
        )
        assert result.cpcb_leach_compliant is True

    def test_high_gypsum_raises_leach(self, model):
        """Higher gypsum fraction should produce higher sulphate leach."""
        low  = model.predict(compressive_strength_mpa=20.0, gypsum_fraction=0.02)
        high = model.predict(compressive_strength_mpa=20.0, gypsum_fraction=0.20)
        assert high.sulphate_leach_mg_per_l > low.sulphate_leach_mg_per_l

    def test_low_hm_capture_raises_hm_leach(self, model):
        """Poor heavy-metal capture increases leach."""
        good = model.predict(compressive_strength_mpa=20.0, heavy_metal_capture_pct=99.0)
        poor = model.predict(compressive_strength_mpa=20.0, heavy_metal_capture_pct=40.0)
        assert poor.heavy_metal_leach_mg_per_l > good.heavy_metal_leach_mg_per_l


class TestCarbonation:
    def test_carbonation_depth_bounded(self, model):
        r = model.predict(compressive_strength_mpa=20.0, block_depth_mm=100.0)
        assert 0.0 <= r.carbonation_depth_10yr_mm <= 100.0

    def test_stronger_block_carbonates_less(self, model):
        """Higher strength → lower porosity → slower carbonation front."""
        weak   = model.predict(compressive_strength_mpa=5.0)
        strong = model.predict(compressive_strength_mpa=35.0)
        assert strong.carbonation_depth_10yr_mm <= weak.carbonation_depth_10yr_mm

    def test_carbonation_index_bounded(self, model):
        r = model.predict(compressive_strength_mpa=20.0)
        assert 0.0 <= r.carbonation_index <= 1.0


class TestOverallGrade:
    def test_excellent_block_gets_grade_a(self, model):
        """Well-performing blocks should grade A+, A, or B."""
        result = model.predict(
            compressive_strength_mpa=32.0,
            water_cement_ratio=0.35,
            chitosan_wt_pct=4.0,
            gypsum_fraction=0.02,
            heavy_metal_capture_pct=99.0,
        )
        assert result.overall_grade in ("A+", "A", "B")

    def test_non_compliant_leach_fails(self, model):
        """CPCB leach failure must result in FAIL grade regardless of strength."""
        result = model.predict(
            compressive_strength_mpa=30.0,
            gypsum_fraction=0.40,        # very high gypsum → SO₄ leach > 250 mg/L
            heavy_metal_capture_pct=20.0, # poor capture
            chitosan_wt_pct=0.5,
        )
        assert result.overall_grade == "FAIL"

    def test_service_life_positive(self, model):
        for strength in [10.0, 20.0, 30.0]:
            r = model.predict(compressive_strength_mpa=strength)
            assert r.service_life_years > 0

    def test_result_is_dataclass(self, model):
        r = model.predict(compressive_strength_mpa=20.0)
        assert isinstance(r, DurabilityResult)
