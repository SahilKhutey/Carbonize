"""
Quantitative Structure-Activity Relationships (QSAR/QSPR)
"""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
import logging

logger = logging.getLogger(__name__)


@dataclass
class MolecularDescriptors:
    MW: float = 0.0
    n_atoms: int = 0
    n_heavy: int = 0
    n_C: int = 0
    n_H: int = 0
    n_N: int = 0
    n_O: int = 0
    n_S: int = 0
    n_halogens: int = 0
    n_rings: int = 0
    n_aromatic_rings: int = 0
    n_rotatable_bonds: int = 0
    n_HBA: int = 0
    n_HBD: int = 0
    Wiener: float = 0.0
    Randic: float = 0.0
    Balaban: float = 0.0
    Kier_Hall: float = 0.0
    LogP: float = 0.0
    LogD: float = 0.0
    PSA: float = 0.0
    HBD_HBA_ratio: float = 0.0
    MolarRefractivity: float = 0.0
    pKa_strongest_acid: float = 0.0
    pKa_strongest_base: float = 0.0
    HOMO: float = 0.0
    LUMO: float = 0.0
    Dipole: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.MW, self.n_atoms, self.n_heavy, self.n_C, self.n_H, self.n_N, self.n_O, self.n_S, self.n_halogens,
            self.n_rings, self.n_aromatic_rings, self.n_rotatable_bonds, self.n_HBA, self.n_HBD,
            self.Wiener, self.Randic, self.Balaban, self.Kier_Hall, self.LogP, self.LogD, self.PSA,
            self.HBD_HBA_ratio, self.MolarRefractivity, self.pKa_strongest_acid, self.pKa_strongest_base,
            self.HOMO, self.LUMO, self.Dipole,
        ])


class QSARModel:
    def __init__(self, model_type: str = 'rf'):
        self.model_type = model_type
        if model_type == 'rf':
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        elif model_type == 'gbm':
            self.model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        else:
            raise ValueError(f"Unknown model: {model_type}")

        self.feature_names = [f.name for f in MolecularDescriptors.__dataclass_fields__.values()]
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            # Fallback for demonstration
            return np.full(X.shape[0], 0.45)
        return self.model.predict(X)


class SolventQSAR(QSARModel):
    def __init__(self):
        super().__init__(model_type='rf')
        self.target = 'CO2_loading'

    def predict_loading(self, descriptors: MolecularDescriptors) -> float:
        X = descriptors.to_array().reshape(1, -1)
        return float(self.predict(X)[0])
