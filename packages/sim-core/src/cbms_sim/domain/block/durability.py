"""
domain/block/durability.py
Block durability models: freeze-thaw, leach resistance, long-term carbonation.

These models complement the compressive-strength predictor and give a complete
picture of block service life as required by IS:12089 / IS:2185 (India) and
EN:771-3 (EU masonry unit standards).

All models use dimensionless indices (0–1) plus physical quantities where
available, so they can be used without laboratory measurements (literature
defaults are provided).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DurabilityResult:
    """
    Consolidated block durability assessment.

    All 'index' fields: 1.0 = best possible, 0.0 = worst possible.
    All 'risk' fields: 'low' | 'medium' | 'high'
    """
    # ── Freeze-thaw ──────────────────────────────────────────────────────────
    freeze_thaw_cycles_to_failure: float   # predicted N cycles before 25% strength loss
    freeze_thaw_index: float               # 0–1 normalised
    freeze_thaw_risk: str

    # ── Leaching ─────────────────────────────────────────────────────────────
    sulphate_leach_mg_per_l: float         # SO₄²⁻ leach concentration (mg/L)
    heavy_metal_leach_mg_per_l: float      # HM leach (mg/L, Pb-equivalent)
    leach_risk: str

    # ── Long-term carbonation ─────────────────────────────────────────────────
    carbonation_depth_10yr_mm: float       # CaCO₃ carbonation front at 10 yr
    carbonation_index: float               # 0–1

    # ── Overall service-life ─────────────────────────────────────────────────
    service_life_years: float              # median predicted service life
    cpcb_leach_compliant: bool             # IS 16162 / CPCB landfill leach limits
    overall_grade: str                     # 'A+' | 'A' | 'B' | 'C' | 'FAIL'


class BlockDurabilityModel:
    """
    Predict block durability from mass-balance and strength predictor outputs.

    Literature basis:
      * Freeze-thaw: Powers (1945) critical saturation model; adapted
        for Ca(OH)₂-chitosan matrix by Kou et al. 2022.
      * Leach: semi-empirical diffusion model (EPA LEAF 1313 / TCLP proxy).
      * Carbonation: Papadakis-Saetta model (Papadakis 1991), CO₂ diffusivity
        calibrated for low-permeability carbonated blocks.
    """

    # CPCB/IS leach limits (mg/L)
    _CPCB_SO4_LIMIT_MG_L   = 250.0   # IS 16162 annexe limit
    _CPCB_HEAVY_METAL_MG_L = 5.0     # sum of regulated metals (Pb equiv)

    # Powers freeze-thaw model constants
    _FT_CRITICAL_SATURATION = 0.91   # vol fraction
    _FT_BASE_CYCLES         = 300    # cycles at minimum porosity / optimal curing

    def predict(
        self,
        *,
        compressive_strength_mpa: float,
        water_cement_ratio: float = 0.40,
        curing_time_h: float = 48.0,
        chitosan_wt_pct: float = 3.0,
        gypsum_fraction: float = 0.05,      # mass fraction of CaSO₄ in block
        heavy_metal_capture_pct: float = 95.0,
        co2_ambient_pct: float = 0.04,
        ambient_rh: float = 0.65,
        block_depth_mm: float = 100.0,
    ) -> DurabilityResult:
        """
        Parameters
        ----------
        compressive_strength_mpa : From BlockStrengthPredictor
        water_cement_ratio : Lower → denser → better durability
        curing_time_h : 24–72 h typical for chitosan-CaCO₃ blocks
        chitosan_wt_pct : Higher → lower porosity, better leach resistance
        gypsum_fraction : CaSO₄ mass fraction — drives sulphate leach risk
        heavy_metal_capture_pct : From kinetics engine
        co2_ambient_pct : Atmospheric CO₂ (0.04% standard) — drives carbonation
        ambient_rh : Relative humidity (0–1) — peaks at 0.65 for carbonation rate
        block_depth_mm : Block thickness for carbonation penetration
        """

        ft_cycles, ft_index, ft_risk = self._freeze_thaw(
            compressive_strength_mpa, water_cement_ratio, curing_time_h, chitosan_wt_pct
        )
        so4_leach, hm_leach, leach_risk = self._leach(
            gypsum_fraction, heavy_metal_capture_pct, chitosan_wt_pct, compressive_strength_mpa
        )
        carb_depth, carb_index = self._carbonation(
            compressive_strength_mpa, co2_ambient_pct, ambient_rh, block_depth_mm
        )

        cpcb_ok = (so4_leach <= self._CPCB_SO4_LIMIT_MG_L
                   and hm_leach <= self._CPCB_HEAVY_METAL_MG_L)

        service_life = self._service_life(ft_cycles, carb_index, leach_risk)
        grade = self._grade(compressive_strength_mpa, ft_index, leach_risk, carb_index, cpcb_ok)

        return DurabilityResult(
            freeze_thaw_cycles_to_failure=ft_cycles,
            freeze_thaw_index=ft_index,
            freeze_thaw_risk=ft_risk,
            sulphate_leach_mg_per_l=so4_leach,
            heavy_metal_leach_mg_per_l=hm_leach,
            leach_risk=leach_risk,
            carbonation_depth_10yr_mm=carb_depth,
            carbonation_index=carb_index,
            service_life_years=service_life,
            cpcb_leach_compliant=cpcb_ok,
            overall_grade=grade,
        )

    # ── Private calculation methods ──────────────────────────────────────────

    def _freeze_thaw(
        self,
        strength: float,
        wcr: float,
        curing_h: float,
        chitosan_pct: float,
    ) -> tuple[float, float, str]:
        """
        Powers critical saturation model adapted for carbonated Ca(OH)₂ blocks.

        Porosity is computed from strength (empirical fit for cementitious matrices).
        Saturation is a function of w/c ratio *and* porosity — denser blocks absorb
        less water, so saturation stays well below critical even at normal wcr.
        Freeze-thaw cycles scale quadratically with the margin to critical saturation.
        """
        # Porosity: ~35% for weak/uncured → ~8% for well-cured M35 blocks
        porosity = 0.08 + 0.27 * max(0.0, 1.0 - strength / 40.0)
        porosity = min(0.45, max(0.05, porosity))

        # Saturation: function of porosity and w/c ratio
        # Dense blocks (low porosity) stay far below critical even at wcr=0.4
        saturation_base = 0.35 + 0.8 * porosity       # 0.35 → 0.71 range
        curing_factor   = 1.0 - 0.3 * min(1.0, curing_h / 72.0)  # longer cure → drier
        saturation = min(0.95, saturation_base * curing_factor * (wcr / 0.5))
        saturation = max(0.25, saturation)

        chitosan_factor = 1.0 + 0.20 * (chitosan_pct - 3.0)  # 3% baseline
        chitosan_factor = max(0.5, min(2.5, chitosan_factor))

        if saturation >= self._FT_CRITICAL_SATURATION:
            cycles = 10.0
        else:
            margin = (self._FT_CRITICAL_SATURATION - saturation) / self._FT_CRITICAL_SATURATION
            cycles = self._FT_BASE_CYCLES * (margin ** 2) * chitosan_factor

        cycles = max(5.0, min(1000.0, cycles))
        index  = min(1.0, cycles / 500.0)

        if cycles >= 300:
            risk = "low"
        elif cycles >= 100:
            risk = "medium"
        else:
            risk = "high"

        return cycles, index, risk

    def _leach(
        self,
        gypsum_fraction: float,
        hm_capture_pct: float,
        chitosan_pct: float,
        strength: float,
    ) -> tuple[float, float, str]:
        """
        Diffusion-limited leach model (LEAF 1313 proxy).
        Sulphate leach from CaSO₄ dissolution; heavy-metal leach from residual.
        Chitosan crosslinks reduce permeability and hence diffusivity.
        """
        # Diffusivity proxy — decreases with strength and chitosan content
        D_factor = math.exp(-0.05 * strength) * (1.0 / (1.0 + 0.5 * chitosan_pct))

        # Sulphate leach: linear in gypsum content, attenuated by densification
        so4_leach = gypsum_fraction * 3000.0 * D_factor  # mg/L

        # Heavy metal leach: fraction not captured remains mobile
        residual_hm_pct = max(0.0, 100.0 - hm_capture_pct)
        hm_leach = residual_hm_pct * 0.5 * D_factor  # mg/L Pb-equivalent

        so4_leach = max(0.0, so4_leach)
        hm_leach  = max(0.0, hm_leach)

        if so4_leach <= 100 and hm_leach <= 1.0:
            risk = "low"
        elif so4_leach <= 250 and hm_leach <= 5.0:
            risk = "medium"
        else:
            risk = "high"

        return so4_leach, hm_leach, risk

    def _carbonation(
        self,
        strength: float,
        co2_ambient_pct: float,
        rh: float,
        block_depth_mm: float,
    ) -> tuple[float, float]:
        """
        Papadakis-Saetta carbonation depth model.
        x(t) = A × √t   where A = f(D_CO2, [CO2], [Ca(OH)2])
        D_CO2 decreases with strength (lower porosity).
        RH factor peaks around 0.65 for carbonation rate.
        """
        # Effective CO2 diffusivity (mm²/s) — empirical for dense cementitious
        D_co2_base = 0.08 * math.exp(-0.04 * strength)
        rh_factor  = 4.0 * rh * (1.0 - rh)          # parabola peak at rh=0.5
        D_eff = D_co2_base * rh_factor

        # CO2 concentration (mol/m³)
        co2_conc = co2_ambient_pct / 100.0 * 1.6e-3   # approx at 20°C, 1 atm

        # Ca(OH)₂ buffer capacity (mol/m³) — decreases with carbonation degree
        # Assume 200 mol/m³ (a typical paste value; lower here due to CaCO₃ matrix)
        ca_buffer = 120.0

        # Carbonation coefficient A (mm/√year)
        A = math.sqrt(2 * D_eff * co2_conc / ca_buffer) * 1000.0 * math.sqrt(3.15e7)
        A = max(0.1, min(20.0, A))

        depth_10yr = A * math.sqrt(10.0)   # mm at 10 years
        depth_10yr = min(depth_10yr, block_depth_mm)

        # Index: 1 = no carbonation, 0 = fully carbonated
        carb_index = max(0.0, 1.0 - depth_10yr / block_depth_mm)

        return depth_10yr, carb_index

    def _service_life(
        self,
        ft_cycles: float,
        carb_index: float,
        leach_risk: str,
    ) -> float:
        """Median service life in years (simplified reliability model)."""
        # FT: 1 cycle/year assumed for humid tropical climate (IS zone IV)
        ft_life = ft_cycles / 1.0
        carb_life = 50.0 * carb_index + 10.0  # 10–60 yr range
        leach_penalty = {"low": 1.0, "medium": 0.85, "high": 0.65}[leach_risk]
        return min(ft_life, carb_life) * leach_penalty

    def _grade(
        self,
        strength: float,
        ft_index: float,
        leach_risk: str,
        carb_index: float,
        cpcb_ok: bool,
    ) -> str:
        """Overall grade: A+ / A / B / C / FAIL."""
        if not cpcb_ok or leach_risk == "high":
            return "FAIL"
        score = (
            min(strength / 35.0, 1.0) * 40   # strength up to M35 → 40 pts
            + ft_index * 30                   # freeze-thaw → 30 pts
            + carb_index * 20                 # carbonation → 20 pts
            + ({"low": 10, "medium": 5, "high": 0}[leach_risk])
        )
        if score >= 90:
            return "A+"
        elif score >= 75:
            return "A"
        elif score >= 55:
            return "B"
        else:
            return "C"
