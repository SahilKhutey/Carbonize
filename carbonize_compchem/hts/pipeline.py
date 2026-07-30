"""
HTVS Virtual Screening Pipeline
"""
from typing import Dict, List

class HTVSPipeline:
    def screen_library(self, candidate_ids: List[str]) -> List[Dict]:
        return [{'id': cid, 'score': 85.0} for cid in candidate_ids]
