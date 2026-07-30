"""
Canonical Reference Architecture Specifications
"""
from typing import Dict

class ReferenceArchitecture:
    @staticmethod
    def get_tier_spec(tier: str = 'medium') -> Dict:
        specs = {
            'small': {'capacity': '<100k t/yr', 'gpus': 1, 'cpus': 8, 'ram_gb': 32, 'storage_tb': 1.0, 'monthly_cloud_cost_usd': 850},
            'medium': {'capacity': '100k - 1M t/yr', 'gpus': 4, 'cpus': 32, 'ram_gb': 128, 'storage_tb': 10.0, 'monthly_cloud_cost_usd': 3400},
            'large': {'capacity': '>1M t/yr', 'gpus': 16, 'cpus': 128, 'ram_gb': 512, 'storage_tb': 100.0, 'monthly_cloud_cost_usd': 12500},
        }
        return specs.get(tier, specs['medium'])
