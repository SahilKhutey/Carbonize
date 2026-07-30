"""
Story Generator for Pitch Demos
"""
from typing import Dict

class StoryGenerator:
    def generate_narrative(self, plant_capacity_t_yr: float = 1_000_000) -> Dict:
        savings_m_yr = (plant_capacity_t_yr / 1_000_000) * 8.0
        return {
            'headline': f'Carbonize delivers ${savings_m_yr:.1f}M annual savings at {plant_capacity_t_yr:,.0f} t/yr scale',
            'summary': f'By replacing standard 30 wt% MEA with SOLV-237, reboiler energy drops from 3.6 to 2.45 GJ/ton CO2, slashing steam OPEX by 32%.',
        }
