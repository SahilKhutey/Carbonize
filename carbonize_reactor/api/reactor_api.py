"""
FastAPI Router for Reactor Engineering API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from ..reactors.base import ReactorGeometry, OperatingConditions, ReactionNetwork
from ..reactors.packed_bed import PackedBedReactor
from ..reactors.trickle_bed import TrickleBedReactor
from ..reactors.monolith import MonolithReactor
from ..reactors.membrane import MembraneReactor
from ..transport.diffusion.porous import thiele_modulus, internal_effectiveness


router = APIRouter(prefix="/v1/reactor", tags=["reactor"])


class ReactorSolveRequest(BaseModel):
    reactor_type: str = 'packed_bed'
    length: float = 2.0
    diameter: float = 0.05
    T_in: float = 573.15
    P_in: float = 200000.0
    flow_gas: float = 10.0
    y_in: Dict[str, float] = {'CO': 0.05, 'O2': 0.21, 'N2': 0.74}


@router.post("/solve")
async def solve_reactor(req: ReactorSolveRequest):
    geom = ReactorGeometry(length=req.length, diameter=req.diameter)
    op = OperatingConditions(T_in=req.T_in, P_in=req.P_in, flow_gas=req.flow_gas, y_in=req.y_in)
    reactions = ReactionNetwork(species=list(req.y_in.keys()) + ['CO2'])

    if req.reactor_type == 'trickle_bed':
        reactor = TrickleBedReactor(geom, op, reactions)
    elif req.reactor_type == 'monolith':
        reactor = MonolithReactor(geom, op, reactions)
    elif req.reactor_type == 'membrane':
        reactor = MembraneReactor(geom, op, reactions)
    else:
        reactor = PackedBedReactor(geom, op, reactions)

    state = reactor.solve(n_points=50)

    return {
        'z': state.z.tolist(),
        'profiles': {s: y.tolist() for s, y in state.y.items()},
        'T_profile': state.T.tolist(),
        'P_profile': state.P.tolist(),
        'conversion': state.conversion,
        'pressure_drop': state.pressure_drop,
        'ghsv': state.ghsv,
        'space_time': state.space_time,
    }


@router.get("/thiele")
async def calculate_thiele(r: float = 0.0015, k: float = 10.0, D_eff: float = 1e-6):
    phi = thiele_modulus(r, k, D_eff)
    eta = internal_effectiveness(phi)
    return {'phi': phi, 'eta': eta}
