"""
Technical Whitepaper Generator
"""
from typing import Dict

def get_whitepaper_metadata() -> Dict:
    return {
        'title': 'AI-Designed Absorbents for Industrial CO2 Capture: A Comparative Study with 30 wt% MEA',
        'authors': ['Carbonize R&D Team', 'DeepMind AI Science'],
        'abstract': 'We present an end-to-end multi-scale computational framework combining equivariant GNNs (MACE/PaiNN), COSMO-RS solvation thermodynamics, and 1D/2D heterogeneous column modeling. When benchmarked across 30+ published experimental absorption datasets, the predicted mass transfer and heat of absorption achieve RMSE < 4.2%.',
    }
