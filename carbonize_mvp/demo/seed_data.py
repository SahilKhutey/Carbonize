"""
Demo Seed Data Generator (CO2 Plants, Solvents, Anomalies)
"""
import numpy as np
from typing import Dict, List


class DemoSeedGenerator:
    def generate_demo_plant(self) -> Dict:
        return {
            'plant_name': 'Rotterdam CCS Facility',
            'capacity_t_yr': 1_000_000,
            'feed_gas': 'Flue Gas (12% CO2)',
            'current_solvent': '30 wt% MEA',
            'annual_opex_usd': 24_500_000,
            'reboiler_duty_gj_t': 3.6,
            'solv_degradation_kg_t': 1.5,
        }

    def generate_top_solvents(() -> List[Dict]):
        return [
            {
                'id': 'SOLV-237',
                'name': 'Sterically Hindered Diamine-Ether',
                'energy_reduction_pct': 32.0,
                'capacity_increase_pct': 18.0,
                'degradation_rate_multiplier': 0.12,
                'reboiler_duty_gj_t': 2.45,
                'heat_of_abs_kj_mol': 62.0,
                'synthesis_time_weeks': 2,
            },
            {
                'id': 'SOLV-109',
                'name': 'Amino Acid Ionic Liquid Blend',
                'energy_reduction_pct': 28.0,
                'capacity_increase_pct': 15.0,
                'degradation_rate_multiplier': 0.08,
                'reboiler_duty_gj_t': 2.59,
                'heat_of_abs_kj_mol': 65.0,
                'synthesis_time_weeks': 3,
            },
        ]
