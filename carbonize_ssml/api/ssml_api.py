"""
FastAPI Router for Solid-State Physics & ML Potentials API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np

from ..electronic.dft import KS_DFT, PlaneWaveBasis, BandStructureAnalyzer
from ..electronic.dos import DOSCalculator
from ..phonons.phonon_dispersion import PhononCalculator, QHA
from ..transport.boltztrap import TransportCalculator
from ..ml_potentials.models.bpnn import BPNN, AtomisticStructure
from ..ml_potentials.models.mace import MACE, MACEConfig
from ..ml_potentials.models.schnet import SchNet, SchNetConfig
from ..ml_potentials.models.painn import PaiNN, PaiNNConfig
from ..ml_potentials.models.ace import ACE, ACEConfig
from ..active_learning.committee import ActiveLearningLoop, CommitteeUncertainty


router = APIRouter(prefix="/api/v1/ssml", tags=["solid-state"])


class BandStructureRequest(BaseModel):
    lattice: List[List[float]] = [[5.0, 0, 0], [0, 5.0, 0], [0, 0, 5.0]]
    atoms: List[Dict] = [{'element': 'Si', 'position': [0, 0, 0]}]
    k_path: List[Dict] = [
        {'label': 'Γ', 'frac': [0, 0, 0]},
        {'label': 'X', 'frac': [0.5, 0, 0]},
        {'label': 'M', 'frac': [0.5, 0.5, 0]},
        {'label': 'Γ', 'frac': [0, 0, 0]},
    ]
    ecutoff: float = 50.0
    functional: str = 'LDA'


class DOSRequest(BaseModel):
    bands: List[List[float]] = [[1.0, 2.0, 3.0]]
    n_electrons: int = 4
    energy_range: List[float] = [-5.0, 10.0]
    sigma: float = 0.05


class TransportRequest(BaseModel):
    bands: List[List[float]] = [[1.0, 2.0, 3.0]]
    fermi_energy: float = 4.2
    temperature: float = 300.0
    mu_range: List[float] = [3.0, 3.5, 4.0, 4.5, 5.0]


@router.post("/band-structure")
async def compute_band_structure(req: BandStructureRequest):
    basis = PlaneWaveBasis(ecutoff=req.ecutoff, lattice=np.array(req.lattice))
    dft = KS_DFT(basis=basis, atoms=req.atoms, functional=req.functional)
    k_path = [(kp['label'], np.array(kp['frac'])) for kp in req.k_path]
    result = dft.compute_band_structure(k_path, n_per_segment=50)
    bands = np.array(result['bands'])
    result['gap_info'] = BandStructureAnalyzer.find_band_gap(bands, result['efermi'])
    return result


@router.post("/dos")
async def compute_dos(req: DOSRequest):
    calc = DOSCalculator(energies=np.array(req.bands), n_electrons=req.n_electrons)
    return calc.compute_total_dos(energy_range=(req.energy_range[0], req.energy_range[1]), sigma=req.sigma)


@router.post("/phonons")
async def compute_phonons():
    phonon = PhononCalculator()
    return phonon.compute_dispersion([])


@router.post("/transport")
async def compute_transport(req: TransportRequest):
    calc = TransportCalculator(bands=np.array(req.bands), fermi_energy=req.fermi_energy, temperature=req.temperature)
    return calc.compute_transport_coefficients(mu_range=np.array(req.mu_range))


@router.post("/active-learning/run")
async def run_active_learning(n_initial: int = 50, n_iterations: int = 5):
    class SampleGen:
        def sample(self): return AtomisticStructure(positions=np.random.uniform(0, 5, (4, 3)), elements=['Si']*4)
    def labeler(s): return -50.0, np.zeros_like(s.positions)

    loop = ActiveLearningLoop(SampleGen(), labeler)
    loop.initialize(n_initial)
    history = loop.run(n_iterations)
    return {'history': history}
