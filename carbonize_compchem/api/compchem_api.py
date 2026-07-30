"""
FastAPI Router for Computational Chemistry & Materials API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np

from ..md.force_fields.opls_aa import OPLSAA
from ..md.force_fields.base import System, Molecule, Atom
from ..md.md_runner import MDRunner, MDConfig
from ..qc.hf import HartreeFock, Molecule_QC, Atom_QC, BasisFunction
from ..qc.dft import DFT
from ..qc.solvation import PCMSolvation, COSMO_Solvation
from ..materials.crystal import CrystalStructure, CrystalBuilder
from ..materials.phase_diagram import PhaseDiagram, Phase
from ..qmmm.mechanical_embedding import QM_MM_Mechanical


router = APIRouter(prefix="/api/v1/compchem", tags=["compchem"])


class MDRequest(BaseModel):
    smiles: List[str] = ['NCCO']
    n_molecules: List[int] = [10]
    box_size: float = 25.0
    dt: float = 0.001
    n_steps: int = 200
    target_T: float = 300.0


class QCRequest(BaseModel):
    atoms: List[Dict] = [{'element': 'O', 'x': 0, 'y': 0, 'z': 0}, {'element': 'H', 'x': 0.75, 'y': 0, 'z': 0.58}]
    basis_set: str = 'sto-3g'
    method: str = 'hf'
    functional: str = 'B3LYP'
    charge: int = 0
    solvent: Optional[str] = None


class CrystalRequest(BaseModel):
    structure_type: str = 'rock_salt'
    element: str = 'Na'
    a: float = 4.0
    b: float = 4.0


@router.post("/md/run")
async def run_md(req: MDRequest):
    ff = OPLSAA()
    molecules = []
    for smiles, n in zip(req.smiles, req.n_molecules):
        mol = ff.build_amine_topology(smiles)
        for _ in range(n):
            molecules.append(mol)
    system = System(molecules=molecules, box=np.eye(3) * req.box_size)
    config = MDConfig(dt=req.dt, n_steps=req.n_steps, target_T=req.target_T)
    runner = MDRunner(system, ff, config)
    results = runner.run()
    return {
        'energies': results.energies,
        'mean_T': float(np.mean(results.temperatures)) if results.temperatures else req.target_T,
        'diffusion_coefficients': results.diffusion_coefficients,
    }


@router.post("/qc/hf")
async def run_hf(req: QCRequest):
    atoms = [Atom_QC(element=a['element'], position=np.array([a.get('x', 0), a.get('y', 0), a.get('z', 0)]) * 1.8897, Z=8 if a['element'] == 'O' else 1, mass=16.0 if a['element'] == 'O' else 1.0) for a in req.atoms]
    basis = [BasisFunction(exponent=0.5, coefficient=1.0, center=a.position) for a in atoms]
    mol = Molecule_QC(atoms=atoms, basis=basis)
    hf = HartreeFock(mol, charge=req.charge)
    res = hf.compute_energy()
    if req.solvent:
        pcm = PCMSolvation(req.solvent)
        res['solvation_energy'] = pcm.compute_solvation_energy(hf)
    return res


@router.post("/qc/dft")
async def run_dft(req: QCRequest):
    atoms = [Atom_QC(element=a['element'], position=np.array([a.get('x', 0), a.get('y', 0), a.get('z', 0)]) * 1.8897, Z=8 if a['element'] == 'O' else 1, mass=16.0 if a['element'] == 'O' else 1.0) for a in req.atoms]
    basis = [BasisFunction(exponent=0.5, coefficient=1.0, center=a.position) for a in atoms]
    mol = Molecule_QC(atoms=atoms, basis=basis)
    dft = DFT(mol, charge=req.charge, functional=req.functional)
    return dft.compute_energy()


@router.post("/materials/crystal")
async def build_crystal(req: CrystalRequest):
    if req.structure_type == 'rock_salt':
        crystal = CrystalBuilder.rock_salt(req.element)
    elif req.structure_type == 'perovskite':
        crystal = CrystalBuilder.perovskite(a=req.a, b=req.b)
    else:
        crystal = CrystalBuilder.graphite()
    return {
        'name': crystal.name,
        'lattice': crystal.lattice.tolist(),
        'volume': crystal.volume,
        'basis': crystal.basis,
    }


@router.post("/materials/phase-diagram")
async def calculate_phase_diagram(system_name: str = 'Fe-C', T_min: float = 300.0, T_max: float = 1800.0):
    diagram = PhaseDiagram(system_name)
    diagram.components = ['Fe', 'C']
    diagram.add_phase(Phase('FCC', 'FCC', ['Fe', 'C'], G_ser={'Fe': -50.0, 'C': -10.0}))
    diagram.add_phase(Phase('LIQUID', 'LIQUID', ['Fe', 'C'], G_ser={'Fe': -30.0, 'C': -5.0}))
    return diagram.binary_phase_diagram((T_min, T_max))
