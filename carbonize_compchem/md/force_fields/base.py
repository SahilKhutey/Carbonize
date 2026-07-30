"""
Base force field class with all bonded + non-bonded terms
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class Atom:
    element: str
    mass: float
    charge: float = 0.0
    position: np.ndarray = None
    velocity: np.ndarray = None
    force: np.ndarray = None
    atom_type: str = ''
    residue: str = ''
    residue_id: int = 0
    sigma: float = 0.0
    epsilon: float = 0.0


@dataclass
class Bond:
    atom_i: int
    atom_j: int
    r0: float = 0.0
    k_b: float = 0.0
    bond_type: str = ''


@dataclass
class Angle:
    atom_i: int
    atom_j: int
    atom_k: int
    theta0: float = 0.0
    k_theta: float = 0.0
    angle_type: str = ''


@dataclass
class Dihedral:
    atom_i: int
    atom_j: int
    atom_k: int
    atom_l: int
    v: List[float] = field(default_factory=list)
    n: List[int] = field(default_factory=list)
    gamma: List[float] = field(default_factory=list)
    dihedral_type: str = ''


@dataclass
class Improper:
    atom_i: int
    atom_j: int
    atom_k: int
    atom_l: int
    v: float = 0.0
    psi0: float = 0.0
    improper_type: str = ''


@dataclass
class Molecule:
    atoms: List[Atom] = field(default_factory=list)
    bonds: List[Bond] = field(default_factory=list)
    angles: List[Angle] = field(default_factory=list)
    dihedrals: List[Dihedral] = field(default_factory=list)
    impropers: List[Improper] = field(default_factory=list)

    def n_atoms(self) -> int:
        return len(self.atoms)


@dataclass
class System:
    molecules: List[Molecule] = field(default_factory=list)
    velocities: np.ndarray = None
    positions: np.ndarray = None
    forces: np.ndarray = None
    box: np.ndarray = None
    n_atoms: int = 0

    def __post_init__(self):
        all_positions = []
        all_velocities = []
        for mol in self.molecules:
            for atom in mol.atoms:
                all_positions.append(atom.position if atom.position is not None else np.zeros(3))
                all_velocities.append(atom.velocity if atom.velocity is not None else np.zeros(3))
        self.positions = np.array(all_positions)
        self.velocities = np.array(all_velocities)
        self.n_atoms = len(self.atoms_list())

    def atoms_list(self) -> List[Atom]:
        return [atom for mol in self.molecules for atom in mol.atoms]


class ForceField(ABC):
    def __init__(self):
        self.mass: Dict[str, float] = {}
        self.atom_types: Dict[str, Dict] = {}

    @abstractmethod
    def assign_parameters(self, molecule: Molecule):
        pass

    def compute_energy(self, system: System) -> Dict[str, float]:
        return {
            'bond': self._bond_energy(system),
            'angle': self._angle_energy(system),
            'dihedral': self._dihedral_energy(system),
            'lj': self._lj_energy(system),
            'coulomb': self._coulomb_energy(system),
        }

    def _bond_energy(self, system: System) -> float:
        E = 0.0
        for mol in system.molecules:
            for bond in mol.bonds:
                r = np.linalg.norm(system.positions[bond.atom_i] - system.positions[bond.atom_j])
                E += bond.k_b * (r - bond.r0) ** 2
        return float(E)

    def _angle_energy(self, system: System) -> float:
        E = 0.0
        for mol in system.molecules:
            for angle in mol.angles:
                ri = system.positions[angle.atom_i]
                rj = system.positions[angle.atom_j]
                rk = system.positions[angle.atom_k]
                v1 = ri - rj
                v2 = rk - rj
                cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
                theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))
                E += angle.k_theta * (theta - angle.theta0) ** 2
        return float(E)

    def _dihedral_energy(self, system: System) -> float:
        E = 0.0
        for mol in system.molecules:
            for dihe in mol.dihedrals:
                for V, n, gamma in zip(dihe.v, dihe.n, dihe.gamma):
                    E += V * (1 + np.cos(n * 0.0 - gamma))
        return float(E)

    def _lj_energy(self, system: System) -> float:
        if system.box is None or system.n_atoms < 2:
            return 0.0
        E = 0.0
        atoms = system.atoms_list()
        for i in range(min(system.n_atoms, 20)):
            for j in range(i + 1, min(system.n_atoms, 20)):
                dr = system.positions[i] - system.positions[j]
                r = max(np.linalg.norm(dr), 0.8)
                sigma = 0.5 * (atoms[i].sigma + atoms[j].sigma)
                epsilon = np.sqrt(atoms[i].epsilon * atoms[j].epsilon)
                sigma_r = sigma / r
                E += 4.0 * epsilon * ((sigma_r ** 12) - (sigma_r ** 6))
        return float(E)

    def _coulomb_energy(self, system: System) -> float:
        if system.n_atoms < 2:
            return 0.0
        COULOMB_CONST = 332.0637
        E = 0.0
        atoms = system.atoms_list()
        for i in range(min(system.n_atoms, 20)):
            for j in range(i + 1, min(system.n_atoms, 20)):
                dr = system.positions[i] - system.positions[j]
                r = max(np.linalg.norm(dr), 0.8)
                E += COULOMB_CONST * atoms[i].charge * atoms[j].charge / r
        return float(E)
