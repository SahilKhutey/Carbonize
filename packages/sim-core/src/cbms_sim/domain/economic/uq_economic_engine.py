"""
Economic UQ Engine: Monte Carlo economic analysis that uses the SAME
samples as the physical simulation, ensuring uncertainty propagates
correctly from chemistry → economics.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from cbms_sim.domain.kinetics import KineticsResult
from cbms_sim.domain.mass_balance.engine import MassBalanceResult
from cbms_sim.domain.economic.engine import EconomicEngine


@dataclass
class EconomicUQResult:
    """Economic result with full uncertainty distribution."""
    
    # Point estimates (means)
    npv_mean: float
    npv_median: float
    npv_std: float
    
    payback_mean: float
    payback_std: float
    
    annual_revenue_mean: float
    annual_revenue_std: float
    
    annual_opex_mean: float
    annual_opex_std: float
    
    # Distributions (full 10K samples)
    npv_samples: np.ndarray
    payback_samples: np.ndarray
    annual_revenue_samples: np.ndarray
    annual_opex_samples: np.ndarray
    
    # Confidence intervals
    npv_ci_90: tuple  # (low, high)
    payback_ci_90: tuple
    npv_probability_positive: float  # P(NPV > 0)
    payback_probability_lt_5y: float  # P(payback < 5 years)
    
    # Sensitivity (which inputs drive financial uncertainty)
    npv_sensitivity_to_co2_capture: float  # dNPV/dCO2_capture
    npv_sensitivity_to_block_strength: float
    npv_sensitivity_to_opex: float
    npv_sensitivity_to_ccts_price: float


class EconomicUQEngine:
    """Run economic analysis using samples from the physical simulation."""
    
    def __init__(self, base_capex: float, lifetime_years: int = 10, 
                 discount_rate: float = 0.11):
        self.engine = EconomicEngine(
            base_capex=base_capex,
            lifetime_years=lifetime_years,
            discount_rate=discount_rate,
        )
        # Cost parameters with uncertainty
        self.cost_params = {
            'ccts_price_mean': 1850,
            'ccts_price_std': 250,  # ±13% uncertainty
            'block_price_mean': 12,
            'block_price_std': 1.5,  # ±12% uncertainty
            'chitosan_cost_mean': 320,
            'chitosan_cost_std': 50,
            'ca_cost_mean': 50000,
            'ca_cost_std': 12000,  # ±24% uncertainty (custom expression)
            'power_cost_mean': 8.5,
            'power_cost_std': 0.5,
            'water_cost_mean': 65,
            'water_cost_std': 8,
            'opex_labor_mean': 1800000,  # annual
            'opex_labor_std': 200000,
            'opex_maint_pct': 0.05,  # 5% of CAPEX
        }
    
    def run(
        self,
        kinetics_samples: list,        # 10K KineticsResult
        mass_balance_samples: list,    # 10K MassBalanceResult
        n_samples: int = 10000,
        random_seed: int = 42,
    ) -> EconomicUQResult:
        """
        Run economic analysis using physical simulation samples.
        
        KEY: The same physics samples drive the financial outcomes,
        ensuring uncertainty propagates correctly.
        """
        rng = np.random.default_rng(random_seed)
        
        # Extract physical KPIs (mean over samples)
        co2_capture_mean = np.mean([k.capture.co2_pct for k in kinetics_samples])
        so2_capture_mean = np.mean([k.capture.so2_pct for k in kinetics_samples])
        block_strength_mean = np.mean([k.capture.block_strength for k in kinetics_samples])
        npv_samples = np.zeros(n_samples)
        payback_samples = np.zeros(n_samples)
        revenue_samples = np.zeros(n_samples)
        opex_samples = np.zeros(n_samples)
        ccts_prices = np.zeros(n_samples)
        
        for i in range(n_samples):
            # 1. Sample cost parameters (from distribution)
            ccts_price = max(0, rng.normal(
                self.cost_params['ccts_price_mean'],
                self.cost_params['ccts_price_std']
            ))
            ccts_prices[i] = ccts_price
            block_price = max(0, rng.normal(
                self.cost_params['block_price_mean'],
                self.cost_params['block_price_std']
            ))
            chitosan_cost = max(0, rng.normal(
                self.cost_params['chitosan_cost_mean'],
                self.cost_params['chitosan_cost_std']
            ))
            ca_cost = max(0, rng.normal(
                self.cost_params['ca_cost_mean'],
                self.cost_params['ca_cost_std']
            ))
            power_cost = max(0, rng.normal(
                self.cost_params['power_cost_mean'],
                self.cost_params['power_cost_std']
            ))
            water_cost = max(0, rng.normal(
                self.cost_params['water_cost_mean'],
                self.cost_params['water_cost_std']
            ))
            opex_labor = max(0, rng.normal(
                self.cost_params['opex_labor_mean'],
                self.cost_params['opex_labor_std']
            ))
            opex_maint = self.cost_params['opex_maint_pct'] * self.engine.base_capex
            
            # 2. Use SAME physical sample (sample i)
            kinetics = kinetics_samples[i % len(kinetics_samples)]
            mb = mass_balance_samples[i % len(mass_balance_samples)]
            
            # 3. Compute revenue from physical output × price
            annual_co2_tons = (
                mb.co2_input_kg_hr * 8000 / 1000 *  # kg to tons
                (kinetics.capture.co2_pct / 100)
            )
            ccts_revenue = annual_co2_tons * ccts_price
            
            blocks_per_year = (
                mb.caco3_output_kg_hr * 8000 / 4 * 0.75  # 4kg blocks, 75% production
            )
            block_revenue = blocks_per_year * block_price
            
            annual_revenue = ccts_revenue + block_revenue
            revenue_samples[i] = annual_revenue
            
            # 4. OPEX from chemistry (depends on inputs consumed)
            annual_opex = (
                mb.chitosan_input_kg_hr * 8000 * chitosan_cost +  # chitosan
                0.1 * 8000 * ca_cost +  # enzyme (reused)
                power_cost * 100 * 8000 +  # power (kWh)
                water_cost * 8.5 * 8000 +  # water
                opex_labor +
                opex_maint
            )
            opex_samples[i] = annual_opex
            
            # 5. NPV
            cashflows = [-self.engine.base_capex] + [annual_revenue - annual_opex] * self.engine.lifetime_years
            npv = sum(cf / (1 + self.engine.discount_rate) ** t 
                     for t, cf in enumerate(cashflows))
            npv_samples[i] = npv
            
            # 6. Payback
            annual_net = annual_revenue - annual_opex
            if annual_net > 0:
                payback_samples[i] = self.engine.base_capex / annual_net * 12  # months
            else:
                payback_samples[i] = float('inf')
        
        # Compute statistics
        npv_valid = npv_samples[npv_samples != float('inf')]
        payback_valid = payback_samples[payback_samples != float('inf')]
        
        result = EconomicUQResult(
            npv_mean=float(np.mean(npv_valid)),
            npv_median=float(np.median(npv_valid)),
            npv_std=float(np.std(npv_valid)),
            
            payback_mean=float(np.mean(payback_valid)),
            payback_std=float(np.std(payback_valid)),
            
            annual_revenue_mean=float(np.mean(revenue_samples)),
            annual_revenue_std=float(np.std(revenue_samples)),
            
            annual_opex_mean=float(np.mean(opex_samples)),
            annual_opex_std=float(np.std(opex_samples)),
            
            npv_samples=npv_samples,
            payback_samples=payback_samples,
            annual_revenue_samples=revenue_samples,
            annual_opex_samples=opex_samples,
            
            npv_ci_90=(float(np.percentile(npv_valid, 5)),
                       float(np.percentile(npv_valid, 95))),
            payback_ci_90=(float(np.percentile(payback_valid, 5)),
                            float(np.percentile(payback_valid, 95))),
            npv_probability_positive=float(np.mean(npv_valid > 0)),
            payback_probability_lt_5y=float(np.mean(payback_valid < 60)),
            
            # Sensitivity: ∂NPV/∂input (numerical)
            npv_sensitivity_to_co2_capture=self._sensitivity(kinetics_samples, 'co2_pct', npv_samples),
            npv_sensitivity_to_block_strength=self._sensitivity(kinetics_samples, 'block_strength', npv_samples),
            npv_sensitivity_to_opex=self._sensitivity(None, 'opex', npv_samples, opex_samples=opex_samples),
            npv_sensitivity_to_ccts_price=self._sensitivity(None, 'ccts_price', npv_samples, ccts_prices=ccts_prices),
        )
        
        return result
    
    def _sensitivity(self, samples, param_name, npv_samples, opex_samples=None, ccts_prices=None):
        """Numerical sensitivity of NPV to parameter via covariance analysis."""
        if param_name == 'co2_pct' and samples:
            x = np.array([k.capture.co2_pct for k in samples])
        elif param_name == 'block_strength' and samples:
            x = np.array([k.capture.block_strength for k in samples])
        elif param_name == 'opex' and opex_samples is not None:
            x = opex_samples
        elif param_name == 'ccts_price' and ccts_prices is not None:
            x = ccts_prices
        else:
            return 0.0

        var_x = np.var(x)
        if var_x < 1e-8:
            return 0.0

        cov_xy = np.cov(x, npv_samples)[0, 1]
        return float(cov_xy / var_x)
