"""
Knowledge Base of Experimental Data & Literature
"""
from typing import Dict, List

class KnowledgeBase:
    def __init__(self):
        self.experiments: List[Dict] = []
        self.papers: List[Dict] = []

    def add_experiment(self, experiment: Dict):
        self.experiments.append(experiment)

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        return [p for p in self.papers if query.lower() in str(p).lower()][:top_k]
