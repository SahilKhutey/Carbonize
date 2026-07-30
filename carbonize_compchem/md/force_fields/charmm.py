"""
CHARMM36 Force Field
"""
from .base import ForceField, Molecule

class CHARMM36(ForceField):
    def assign_parameters(self, molecule: Molecule):
        pass
