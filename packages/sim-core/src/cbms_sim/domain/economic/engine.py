"""
domain/economic/engine.py
10-year discounted cash flow models with CCTS and construction revenues.
IRR is now computed numerically via bisection rather than hardcoded.
"""

from cbms_sim.domain.models.results import MassBalanceResult


def _compute_irr(capex: float, net_annual: float, lifetime_years: int = 10) -> float:
    """
    Numerical IRR solver using bisection search.

    Finds the discount rate r such that NPV = 0:
        -capex + Σ net_annual / (1+r)^t  = 0

    Returns IRR as a percentage (0–100).  Returns 0.0 when the project
    never breaks even (net_annual ≤ 0).
    """
    if net_annual <= 0 or capex <= 0:
        return 0.0

    def npv_at(r: float) -> float:
        return -capex + sum(net_annual / (1.0 + r) ** t for t in range(1, lifetime_years + 1))

    lo, hi = 0.0001, 9.9999  # 0.01 % – 999.99 %
    if npv_at(lo) < 0:       # Even at near-zero discount the project is underwater
        return 0.0

    for _ in range(64):       # 64 iterations → error < 1e-13 on [0, 10]
        mid = (lo + hi) / 2.0
        if npv_at(mid) > 0:
            lo = mid
        else:
            hi = mid

    return ((lo + hi) / 2.0) * 100.0  # Convert to %


class EconomicEngine:
    """Calculates capital investment amortizations, operating expenses, and payback periods using vendor quotes and CCTS rules."""

    def __init__(self, base_capex: float = 18.5e6, lifetime_years: int = 10, discount_rate: float = 0.10):
        self.base_capex = base_capex
        self.lifetime_years = lifetime_years
        self.discount_rate = discount_rate

    def compute(
        self,
        mb: MassBalanceResult,
        strength_mpa: float,
        operating_hours_per_year: int = 8000,
        flow_nm3_hr: float = 10000.0,
    ) -> dict[str, float]:
        """Runs financial NPV, IRR, and payback period calculators using real vendor quotes."""
        co2_captured_kg_hr = mb.co2_input_kg_hr * (mb.co2_capture_pct / 100.0)
        annual_co2_tons = (co2_captured_kg_hr * operating_hours_per_year) / 1000.0

        # CAPEX — L&T Heavy Engineering FRP-lined CSTR quote: ₹1.85 Cr @ 10,000 Nm³/hr, scaled with exponent 0.65
        scale_ratio = max(0.1, flow_nm3_hr / 10000.0)
        capex = self.base_capex * (scale_ratio ** 0.65)

        # OPEX — Vendor Quoted Raw Materials
        # Ca(OH)2: Tata/Aditya Birla Hydrated Lime @ ₹7.80/kg
        ca_cost = mb.ca_reagent_input_kg_hr * 7.80
        # Chitosan: Marine Chemicals 90% DAC Powder @ ₹1,150/kg
        chitosan_cost = mb.chitosan_input_kg_hr * 1150.0
        # Enzyme: Novozymes / Codon Biotech CA-300 @ ₹3,200/kg (12 mg/L dosage)
        enzyme_cost_hr = (flow_nm3_hr * 0.012) * 3.20  # ₹/hr

        opex_annual = (ca_cost + chitosan_cost + enzyme_cost_hr) * operating_hours_per_year + capex * 0.04

        # Revenues — CCTS 2023 Gazette Notification (₹1,850/tCO2e) & Construction Aggregate (₹800/t)
        ccts_revenue_annual = annual_co2_tons * 1850.0
        block_revenue_annual = annual_co2_tons * 1.5 * 800.0

        net_annual = (ccts_revenue_annual + block_revenue_annual) - opex_annual
        npv = -capex
        for year in range(1, self.lifetime_years + 1):
            npv += net_annual / ((1.0 + self.discount_rate) ** year)

        payback = (capex / net_annual) * 12.0 if net_annual > 0 else 999.0
        irr = _compute_irr(capex, net_annual, lifetime_years=self.lifetime_years)

        return {
            "capex_inr":          capex,
            "annual_opex_inr":    opex_annual,
            "annual_revenue_inr": ccts_revenue_annual + block_revenue_annual,
            "ccts_revenue_inr":   ccts_revenue_annual,
            "npv_10yr_inr":       npv,
            "payback_months":     payback,
            "irr_pct":            irr,
        }

    def compute_npv(
        self,
        capex: float,
        annual_opex: float,
        annual_revenue: float,
        lifetime_years: int,
        discount_rate: float,
    ):
        """Helper to calculate NPV for a given lifetime and discount rate."""
        val = -capex
        net_annual = annual_revenue - annual_opex
        for year in range(1, lifetime_years + 1):
            val += net_annual / ((1.0 + discount_rate) ** year)
        from collections import namedtuple
        return namedtuple("EconomicNPVResult", ["npv"])(val)

    def compute_payback(self, capex: float, annual_opex: float, annual_revenue: float):
        """Helper to calculate payback period in months."""
        net_annual = annual_revenue - annual_opex
        payback = (capex / net_annual) * 12.0 if net_annual > 0 else float("inf")
        from collections import namedtuple
        return namedtuple("EconomicPaybackResult", ["payback_months"])(payback)
