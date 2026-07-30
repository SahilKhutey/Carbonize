"""
TraPPE Force Field for Small Molecules and VLE
"""
from .base import ForceField, Molecule

class TraPPE(ForceField):
    def assign_parameters(self, molecule: Molecule):
        pass
