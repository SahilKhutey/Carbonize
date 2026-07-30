"""
15-Slide Investor Pitch Deck Structure
"""
from typing import List, Dict

def get_pitch_deck_slides() -> List[Dict]:
    return [
        {'slide': 1, 'title': 'Title', 'headline': 'Carbonize: AI-Designed Chemistry for Industrial Carbon Capture'},
        {'slide': 2, 'title': 'The Problem', 'headline': 'Carbon capture costs $50/ton. Solvent is 30-50% of OPEX; amine degradation slashes capture efficiency 10%/yr.'},
        {'slide': 3, 'title': 'Why Now', 'headline': 'Net-zero mandates & IRA $85/ton tax credits create $40B addressable market across 600+ facilities.'},
        {'slide': 4, 'title': 'Solution', 'headline': 'Virtual screening of 10,000+ solvents/day using equivariant ML potentials & closed-loop discovery.'},
        {'slide': 5, 'title': 'Chemistry AI', 'headline': 'Lead discovery in 2 weeks instead of 2 years with 92% validated prediction accuracy.'},
        {'slide': 6, 'title': 'Case Study (SOLV-237)', 'headline': '32% less energy, 18% higher capacity, 8x slower degradation vs standard 30 wt% MEA.'},
        {'slide': 7, 'title': 'Financial ROI', 'headline': '$8M/year OPEX savings at 1M t/yr plant with a < 6-month payback period.'},
        {'slide': 8, 'title': 'Product & Digital Twin', 'headline': 'Real-time telemetry, predictive maintenance, and chaos engineering resilience.'},
        {'slide': 9, 'title': 'Traction & Pilots', 'headline': '3 signed pilot LOIs in cement and steel sectors for Q1 deployment.'},
        {'slide': 10, 'title': 'Market Opportunity', 'headline': '$15B TAM, $3.2B SAM, $450M SOM by Year 5.'},
        {'slide': 11, 'title': 'Business Model', 'headline': 'SaaS platform fee + per-ton CO2 capture performance share.'},
        {'slide': 12, 'title': 'Competitive Moat', 'headline': 'Proprietary COSMO-RS & DFT datasets, multi-scale reactor solvers, and hardware twin.'},
        {'slide': 13, 'title': 'Team', 'headline': 'PhD computational chemists and senior ML systems engineers.'},
        {'slide': 14, 'title': 'Financial Ask', 'headline': 'Raising $5.0M Series A for 18-month runway to reach $2.5M ARR.'},
        {'slide': 15, 'title': 'Appendix', 'headline': 'Detailed benchmark data, SOC 2 compliance package, and reference architectures.'},
    ]
