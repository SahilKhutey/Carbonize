"""
Guided Demo Tour Scenarios
"""
from typing import List, Dict

def get_demo_steps() -> List[Dict]:
    return [
        {
            'step': 1,
            'minute': '0-2',
            'title': 'The Problem',
            'subtitle': 'Carbon capture costs $40-80/ton. Solvent is 30-50% of OPEX.',
            'focus': '600+ global plants lose 10% efficiency annually due to amine degradation.',
        },
        {
            'step': 2,
            'minute': '2-4',
            'title': 'Our Approach',
            'subtitle': 'AI-driven virtual screening of 10,000+ candidate absorbents per day.',
            'focus': 'Evaluate molecular descriptors & VLE before spending $50k on lab synthesis.',
        },
        {
            'step': 3,
            'minute': '4-6',
            'title': 'Top Candidate: SOLV-237',
            'subtitle': '32% less energy, 18% higher capacity, 8x slower degradation.',
            'focus': 'Synthesized in 2 weeks vs 2 years traditional R&D.',
        },
        {
            'step': 4,
            'minute': '6-8',
            'title': 'Full Plant Impact (ROI)',
            'subtitle': '$8M/year OPEX savings for a 1M ton/year facility.',
            'focus': 'Payback period under 6 months; $64M 10-year cumulative NPV.',
        },
        {
            'step': 5,
            'minute': '8-9',
            'title': 'Digital Twin & Operations',
            'subtitle': 'Real-time telemetry, predictive maintenance, and chaos engineering.',
            'focus': '92% resilience score & failure detection 3 days before SCADA alarms.',
        },
        {
            'step': 6,
            'minute': '9-10',
            'title': 'Proof & Pilot LOI',
            'subtitle': 'Validated against 30+ published datasets with 92% prediction accuracy.',
            'focus': '3 active pilot LOIs for Q1 deployment.',
        },
    ]
