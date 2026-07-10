"""
core/economic_engine.py
Computes CAPEX, OPEX, revenue streams, and payback period
for the biomimetic capture system.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict
from core.config import CONFIG
from core.mass_balance import MassBalanceResult


@dataclass
class FinancialResult:
    """Financial summary output."""
    # Annualized metrics
    annual_co2_captured_tons: float
    annual_block_yield_count: int
    annual_ccts_revenue_inr: float
    annual_block_revenue_inr: float
    annual_opex_inr: float
    annual_net_revenue_inr: float

    # Capital costs
    capex_total_inr: float
    capex_breakdown: Dict[str, float]

    # Payback analysis
    simple_payback_months: float
    npv_10yr_inr: float
    irr_pct: float

    # Sensitivity
    breakeven_carbon_price_inr: float
    breakeven_block_price_inr: float


def compute_capex(
    flow_nm3_per_hr: float,
    system_type: str = "standard_10kNm3",
) -> Dict[str, float]:
    """
    Estimate capital expenditure breakdown for a given plant capacity.
    Cost scaling follows 0.6 power law (typical for chemical process equipment).
    """
    # Reference cost for 10,000 Nm³/hr system
    ref_cost = {
        "stage1_quench": 4_500_000,
        "stage3_reactor": 12_000_000,   # Mesh stack + tower
        "stage4_press": 6_500_000,
        "stage2_mixer": 1_800_000,
        "instrumentation": 3_200_000,   # PLC, sensors, CEMS
        "piping_valves": 2_800_000,
        "civil_foundation": 3_500_000,
        "engineering_pmarg": 1_800_000,
        "contingency_15pct": 0.0,        # Computed below
    }
    ref_cost["contingency_15pct"] = sum(v for k, v in ref_cost.items()
                                        if k != "contingency_15pct") * 0.15

    # Scale by capacity
    scale = (flow_nm3_per_hr / 10_000.0) ** 0.6
    scaled = {k: v * scale for k, v in ref_cost.items()}
    return scaled


def compute_annual_opex(
    mass_balance: MassBalanceResult,
    flow_nm3_per_hr: float,
    hours_per_year: float = 8000.0,
) -> float:
    """Annual operating expense calculation."""
    eco = CONFIG.economic

    # Reagent costs
    chitosan_cost = (mass_balance.chitosan_lattice
                     * hours_per_year * eco.CHITOSAN_FLAKE_PRICE_INR)
    ca_cost = (mass_balance.ca_reagent_input
               * hours_per_year * eco.CALCIUM_HYDROXIDE_PRICE_INR / 1000.0)

    # Utilities
    # Power: ID fan (15 kW) + pumps (8 kW) + press (12 kW) ≈ 35 kW total
    power_kw = 35.0 * (flow_nm3_per_hr / 10_000.0)
    power_cost = power_kw * hours_per_year * eco.ELECTRICITY_TARIFF_INR

    # Water: 1.5 L/Nm³ process water
    water_kl_hr = flow_nm3_per_hr * 1.5 / 1000.0
    water_cost = water_kl_hr * hours_per_year * eco.WATER_TARIFF_INR

    # Enzyme replenishment (5% per month due to deactivation)
    enzyme_replenish_kg_hr = 0.6  # At baseline
    enzyme_cost = (enzyme_replenish_kg_hr * hours_per_year
                   * eco.CHITOSAN_FLAKE_PRICE_INR * 0.3)  # Enzyme costs 30% of chitosan

    # Labor + Maintenance
    labor = 1_800_000  # 3 operators @ ₹50k/mo
    maintenance = 1_200_000

    return (chitosan_cost + ca_cost + power_cost + water_cost
            + enzyme_cost + labor + maintenance)


def run_financial_analysis(
    mass_balance: MassBalanceResult,
    flow_nm3_per_hr: float,
    hours_per_year: float = 8000.0,
    project_lifespan_years: int = 10,
) -> FinancialResult:
    """Full financial model: revenues, costs, payback, NPV, IRR."""
    eco = CONFIG.economic
    capex = compute_capex(flow_nm3_per_hr)
    capex_total = sum(capex.values())

    opex = compute_annual_opex(mass_balance, flow_nm3_per_hr, hours_per_year)

    # Revenue streams
    annual_co2_tons = mass_balance.captured_co2_total * hours_per_year / 1000.0
    ccts_revenue = annual_co2_tons * eco.CCTS_CARBON_PRICE_INR

    # Block yield: assume 4 kg per block, 75% production efficiency
    block_mass_kg_hr = (mass_balance.caco3_output + mass_balance.fly_ash_captured
                        + mass_balance.gypsum_output + mass_balance.chitosan_lattice)
    annual_block_count = int(block_mass_kg_hr * hours_per_year / 4.0 * 0.75)
    block_revenue = annual_block_count * eco.BRICK_MARKET_PRICE_INR

    net_revenue = ccts_revenue + block_revenue - opex

    # Simple payback
    if net_revenue > 0:
        payback_months = (capex_total / net_revenue) * 12.0
        cash_flows = [-capex_total] + [net_revenue] * project_lifespan_years
        
        # IRR (approximate via bisection)
        def npv_at_rate(r):
            return sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))

        lo, hi = -0.99, 2.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if npv_at_rate(mid) > 0:
                lo = mid
            else:
                hi = mid
        irr = mid * 100.0
    else:
        payback_months = float("inf")
        irr = -100.0
        cash_flows = [-capex_total] + [net_revenue] * project_lifespan_years

    # NPV calculation
    discount_rate = eco.DISCOUNT_RATE_ANNUAL
    npv = sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows))

    # Breakeven prices
    breakeven_carbon = (opex - block_revenue) / annual_co2_tons if annual_co2_tons > 0 else float("inf")
    breakeven_block = (opex - ccts_revenue) / annual_block_count if annual_block_count > 0 else float("inf")

    return FinancialResult(
        annual_co2_captured_tons=annual_co2_tons,
        annual_block_yield_count=annual_block_count,
        annual_ccts_revenue_inr=ccts_revenue,
        annual_block_revenue_inr=block_revenue,
        annual_opex_inr=opex,
        annual_net_revenue_inr=net_revenue,
        capex_total_inr=capex_total,
        capex_breakdown=capex,
        simple_payback_months=payback_months,
        npv_10yr_inr=npv,
        irr_pct=irr,
        breakeven_carbon_price_inr=breakeven_carbon,
        breakeven_block_price_inr=breakeven_block,
    )
