"""
Emission compliance checking against regulatory limits
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ComplianceResult:
    compliant: bool
    exceeded: List[Dict]
    margin: Dict[str, float]


class ComplianceEngine:
    """Check emissions against EPA & EU regulatory limits."""
    
    EPA_LIMITS = {
        'NOx': 30.0,
        'SO2': 30.0,
        'PM': 9.0,
        'Hg': 0.003,
    }
    
    EU_LIMITS = {
        'NOx': 50.0,
        'SO2': 35.0,
        'PM': 5.0,
        'Hg': 0.03,
    }
    
    @classmethod
    def check_compliance(cls, emissions: Dict[str, float], region: str = 'EPA') -> ComplianceResult:
        limits = cls.EPA_LIMITS if region == 'EPA' else cls.EU_LIMITS
        exceeded = []
        margin = {}
        
        for pollutant, value in emissions.items():
            if pollutant in limits:
                limit = limits[pollutant]
                if value > limit:
                    exceeded.append({
                        'pollutant': pollutant,
                        'value': value,
                        'limit': limit,
                        'exceedance_percent': ((value - limit) / limit) * 100.0,
                    })
                margin[pollutant] = max(0.0, (limit - value) / limit * 100.0)
        
        return ComplianceResult(
            compliant=len(exceeded) == 0,
            exceeded=exceeded,
            margin=margin,
        )
