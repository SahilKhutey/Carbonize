"""
OPLS-AA Force Field for Amines and Organic Liquids
"""
import numpy as np
from typing import Dict, List, Tuple
from .base import ForceField, Atom, Bond, Angle, Dihedral, Molecule, System


class OPLSAA(ForceField):
    def __init__(self):
        super().__init__()
        self.mass = {'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'S': 32.065}
        self.atom_types = {
            'CT': {'charge': 0.14, 'sigma': 3.500, 'epsilon': 0.066, 'mass': 12.011},
            'HC': {'charge': 0.06, 'sigma': 2.500, 'epsilon': 0.030, 'mass': 1.008},
            'NT': {'charge': -0.90, 'sigma': 3.250, 'epsilon': 0.170, 'mass': 14.007},
            'HT': {'charge': 0.40, 'sigma': 2.500, 'epsilon': 0.030, 'mass': 1.008},
            'OH': {'charge': -0.66, 'sigma': 2.960, 'epsilon': 0.210, 'mass': 15.999},
        }

    def assign_parameters(self, molecule: Molecule):
        for atom in molecule.atoms:
            t = 'HC' if atom.element == 'H' else ('NT' if atom.element == 'N' else ('OH' if atom.element == 'O' else 'CT'))
            p = self.atom_types[t]
            atom.atom_type = t
            atom.charge = p['charge']
            atom.sigma = p['sigma']
            atom.epsilon = p['epsilon']
            atom.mass = p['mass']

    def build_amine_topology(self, smiles: str) -> Molecule:
        atoms = [
            Atom('N', 14.007, position=np.array([0.0, 0.0, 0.0])),
            Atom('C', 12.011, position=np.array([1.4, 0.0, 0.0])),
            Atom('C', 12.011, position=np.array([2.5, 1.2, 0.0])),
            Atom('O', 15.999, position=np.array([3.8, 1.2, 0.0])),
        ]
        bonds = [
            Bond(0, 1, r0=1.47, k_b=337.0),
            Bond(1, 2, r0=1.53, k_b=268.0),
            Bond(2, 3, r0=1.43, k_b=320.0),
        ]
        angles = [
            Angle(0, 1, 2, theta0=np.radians(111.3), k_theta=63.0),
            Angle(1, 2, 3, theta0=np.radians(111.5), k_theta=50.0),
        ]
        dihedrals = [
            Dihedral(0, 1, 2, 3, v=[0.3], n=[3], gamma=[0.0]),
        ]
        mol = Molecule(atoms=atoms, bonds=bonds, angles=angles, dihedrals=dihedrals)
        self.assign_parameters(mol)
        return mol
