"""
Active Learning Materials Screener
"""
from typing import Dict, List

class MaterialsScreener:
    def rank_materials(self, materials: List[Dict]) -> List[Dict]:
        return sorted(materials, key=lambda m: m.get('score', 0.0), reverse=True)
