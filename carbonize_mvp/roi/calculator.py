"""
Interactive ROI & Financial Savings Model
"""
import numpy as np
from typing import Dict


class ROICalculator:
    def calculate(self, 
                  capacity_t_yr: float = 1_000_000,
                  steam_cost_usd_gj: float = 15.0,
                  solvent_cost_usd_kg: float = 3.50,
                  co2_tax_credit_usd_t: float = 85.0) -> Dict:
        """
        Calculate financial metrics for switching from MEA to SOLV-237.
        """
        # ─── Baseline MEA ─────────────────────────────────────────
        mea_reboiler_gj_t = 3.6
        mea_degradation_kg_t = 1.5
        mea_steam_cost = capacity_t_yr * mea_reboiler_gj_t * steam_cost_usd_gj
        mea_solv_cost = capacity_t_yr * mea_degradation_kg_t * solvent_cost_usd_kg
        total_mea_opex = mea_steam_cost + mea_solv_cost

        # ─── SOLV-237 ─────────────────────────────────────────────
        solv_reboiler_gj_t = 2.45
        solv_degradation_kg_t = 0.18
        solv_steam_cost = capacity_t_yr * solv_reboiler_gj_t * steam_cost_usd_gj
        solv_solv_cost = capacity_t_yr * solv_degradation_kg_t * (solvent_cost_usd_kg * 1.5)
        total_solv_opex = solv_steam_cost + solv_solv_cost

        # ─── Savings ──────────────────────────────────────────────
        annual_savings = total_mea_opex - total_solv_opex
        retrofitting_capex = capacity_t_yr * 3.5  # $3.50 per ton installed capex
        payback_months = (retrofitting_capex / annual_savings) * 12 if annual_savings > 0 else 999.0
        
        # 10-Year NPV at 8% discount rate
        discount_rate = 0.08
        npv_10yr = sum(annual_savings / ((1 + discount_rate) ** t) for t in range(1, 11)) - retrofitting_capex

        return {
            'capacity_t_yr': capacity_t_yr,
            'annual_savings_usd': float(annual_savings),
            'retrofitting_capex_usd': float(retrofitting_capex),
            'payback_months': float(payback_months),
            'npv_10yr_usd': float(npv_10yr),
            'energy_savings_pct': 31.9,
            'degradation_savings_pct': 84.6,
            'mea_opex_usd': float(total_mea_opex),
            'solv237_opex_usd': float(total_solv_opex),
        }
