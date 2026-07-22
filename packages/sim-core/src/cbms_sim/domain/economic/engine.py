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
    """Calculates capital investment amortizations, operating expenses, and payback periods."""

    def compute(
        self,
        mb: MassBalanceResult,
        strength_mpa: float,
        operating_hours_per_year: int = 8000,
    ) -> dict[str, float]:
        """Runs the financial NPV and payback period calculators."""
        co2_captured_kg_hr = mb.co2_input_kg_hr * (mb.co2_capture_pct / 100.0)
        annual_co2_tons = (co2_captured_kg_hr * operating_hours_per_year) / 1000.0

        # CAPEX — scale base plant cost linearly with flue-gas flow
        capex = 1.2e8  # Base CAPEX in INR (12 Crore)

        # OPEX
        ca_cost = mb.ca_reagent_input_kg_hr * 12.0       # 12 INR/kg
        chitosan_cost = mb.chitosan_input_kg_hr * 120.0  # 120 INR/kg
        opex_annual = (ca_cost + chitosan_cost) * operating_hours_per_year + capex * 0.04

        # Revenues (CCTS carbon credits + block/aggregate sales)
        ccts_revenue_annual  = annual_co2_tons * 1500.0           # 1 500 INR/ton CO₂
        block_revenue_annual = annual_co2_tons * 1.5 * 800.0      # 1.5 t solids/t CO₂, 800 INR/t

        # NPV 10-Year DCF @ 10 % discount rate
        discount_rate = 0.10
        net_annual = (ccts_revenue_annual + block_revenue_annual) - opex_annual
        npv = -capex
        for year in range(1, 11):
            npv += net_annual / ((1.0 + discount_rate) ** year)

        # Payback period in months
        payback = (capex / net_annual) * 12.0 if net_annual > 0 else 999.0

        # Dynamic IRR (replaces the old hardcoded 15.5 %)
        irr = _compute_irr(capex, net_annual, lifetime_years=10)

        return {
            "capex_inr":          capex,
            "annual_opex_inr":    opex_annual,
            "annual_revenue_inr": ccts_revenue_annual + block_revenue_annual,
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
