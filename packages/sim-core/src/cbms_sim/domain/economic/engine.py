"""
domain/economic/engine.py
Implements 10-year discounted cash flow models with CCTS and construction revenues.
"""

from cbms_sim.domain.models.results import MassBalanceResult

class EconomicEngine:
    """Calculates capital investment amortizations, operating expenses, and payback periods."""
    
    def compute(
        self,
        mb: MassBalanceResult,
        strength_mpa: float,
        operating_hours_per_year: int = 8000
    ) -> dict[str, float]:
        """Runs the financial NPV and payback period calculators."""
        co2_captured_kg_hr = mb.co2_input_kg_hr * (mb.co2_capture_pct / 100.0)
        annual_co2_tons = (co2_captured_kg_hr * operating_hours_per_year) / 1000.0
        
        # Scale CAPEX based on flue gas flow sizing
        capex = 1.2e8  # Base CAPEX in INR (12 Crore)
        
        # OPEX scale
        ca_cost = mb.ca_reagent_input_kg_hr * 12.0  # 12 INR/kg
        chitosan_cost = mb.chitosan_input_kg_hr * 120.0  # 120 INR/kg
        opex_annual = (ca_cost + chitosan_cost) * operating_hours_per_year + capex * 0.04
        
        # Revenues (CCTS + Block sales)
        ccts_revenue_annual = annual_co2_tons * 1500.0  # 1500 INR/ton
        block_revenue_annual = annual_co2_tons * 1.5 * 800.0  # 1.5 ton solids per ton CO2, 800 INR/ton
        
        net_annual_cashflow = (ccts_revenue_annual + block_revenue_annual) - opex_annual
        
        # NPV 10-Year Discounted Cash Flow at 10%
        discount_rate = 0.10
        npv = -capex
        for year in range(1, 11):
            npv += net_annual_cashflow / ((1.0 + discount_rate) ** year)
            
        # Payback period in months
        if net_annual_cashflow > 0:
            payback = (capex / net_annual_cashflow) * 12.0
        else:
            payback = 999.0
            
        return {
            "capex_inr": capex,
            "annual_opex_inr": opex_annual,
            "annual_revenue_inr": ccts_revenue_annual + block_revenue_annual,
            "npv_10yr_inr": npv,
            "payback_months": payback
        }
