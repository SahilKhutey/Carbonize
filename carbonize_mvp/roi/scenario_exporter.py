"""
Scenario One-Pager Exporter
"""
from typing import Dict

def generate_one_pager_summary(roi_result: Dict) -> Dict:
    return {
        'title': 'Carbonize Solvent Switch Business Case',
        'plant_scale': f"{roi_result.get('capacity_t_yr', 1000000):,.0f} t/yr",
        'annual_savings': f"${roi_result.get('annual_savings_usd', 8000000)/1e6:.2f}M / year",
        'payback': f"{roi_result.get('payback_months', 5.2):.1f} months",
        'npv_10yr': f"${roi_result.get('npv_10yr_usd', 64000000)/1e6:.1f}M",
    }
