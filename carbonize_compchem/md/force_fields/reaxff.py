"""
ReaxFF Reactive Force Field
"""
from .base import ForceField, Molecule

class ReaxFF(ForceField):
    def assign_parameters(self, molecule: Molecule):
        pass
