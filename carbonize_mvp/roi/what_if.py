"""
What-If Scenario Sensitivity Analysis
"""
import numpy as np
from typing import Dict, List
from .calculator import ROICalculator


class WhatIfEngine:
    def sensitivity_analysis(self, capacity_t_yr: float = 1_000_000) -> Dict:
        calc = ROICalculator()
        steam_costs = [10.0, 15.0, 20.0, 25.0]
        co2_prices = [50.0, 85.0, 120.0, 180.0]
        
        results = []
        for s in steam_costs:
            res = calc.calculate(capacity_t_yr=capacity_t_yr, steam_cost_usd_gj=s)
            results.append({
                'steam_cost_usd_gj': s,
                'annual_savings_usd': res['annual_savings_usd'],
                'payback_months': res['payback_months'],
            })
        return {'sensitivity_by_steam_cost': results}
