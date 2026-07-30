"""
Pilot Customer Letter of Intent (LOI) Template
"""
from typing import Dict

def get_loi_template(company_name: str = 'Global Cement Corp', plant_location: str = 'Rotterdam, NL') -> Dict:
    return {
        'company_name': company_name,
        'plant_location': plant_location,
        'scope': '3-Month Pilot Evaluation of SOLV-237 Absorbent & Carbonize Digital Twin',
        'terms': [
            'Carbonize provides 500L SOLV-237 batch and deploys edge telemetry gateway.',
            'Pilot customer provides slipstream access (10,000 Nm³/h flue gas).',
            'Target success criteria: >25% reduction in reboiler steam usage vs MEA.',
            'Upon meeting criteria, customer holds option to convert to 3-year commercial SaaS license.',
        ],
        'signee': 'Chief Operating Officer / VP Decarbonization',
    }
