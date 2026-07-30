"""
FastAPI Router for Chemistry Experimentation Platform API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid

from ..molecular_design.solvent_designer import COSMORS_SolventDesigner, AmineMixtureDesigner
from ..molecular_design.catalyst_designer import CatalystDesigner, AdsorbentDesigner
from ..molecular_design.qsar_model import QSARModel, MolecularDescriptors
from ..doe.factorial import FullFactorial, FractionalFactorial, CentralComposite, BoxBehnken, PlackettBurman, ExperimentalFactor
from ..doe.sampling import LatinHyperCube, SobolSampling
from ..doe.sequential import BayesianOptimizer
from ..lims.sample import SampleRegistry, Sample, HazardClass
from ..lims.experiment import Experiment, CO2AbsorptionSOP, ViscosityMeasurementSOP
from ..lims.instrument import FTIRInstrument, GCMSInstrument, HPLCInstrument, pHMeter, Balance, MeasurementConfig
from ..pilot.rig import PilotRig, RigSpec, RigOperatingPoint
from ..safety.hazop import CO2AbsorptionHAZOP, LOPA
from ..safety.ghs import get_classification, KNOWN_CLASSIFICATIONS
from ..discovery.hypothesis_generator import HypothesisGenerator, KnowledgeBase


router = APIRouter(prefix="/api/v1/lab", tags=["lab"])

sample_registry = SampleRegistry()
knowledge_base = KnowledgeBase()
experiments_db: Dict[str, Experiment] = {}


class SolventDesignRequest(BaseModel):
    amine_type: str = 'primary'
    additional_groups: List[str] = []
    n_candidates: int = 5


class CatalystDesignRequest(BaseModel):
    target_conversion: float = 0.95
    operating_T: float = 623.0
    reaction_type: str = 'NOx_SCR'


class DoERequest(BaseModel):
    design_type: str
    factors: List[Dict]
    options: Dict = {}


class SampleRegisterRequest(BaseModel):
    name: str
    cas_number: str = ''
    formula: str = ''
    purity: float = 0.0
    supplier: str = ''
    ghs_class: str = ''
    quantity: float = 0.0
    units: str = 'kg'
    storage_location: str = ''


@router.post("/molecular/solvent/design")
async def design_solvent(req: SolventDesignRequest):
    designer = COSMORS_SolventDesigner()
    candidates = [designer.screen_amine_solvent(req.amine_type, req.additional_groups) for _ in range(req.n_candidates)]
    candidates.sort(key=lambda c: -c.overall_score)
    return {
        'candidates': [
            {
                'name': c.name,
                'CO2_loading_max': c.CO2_loading_max,
                'cyclic_capacity': c.cyclic_capacity,
                'regeneration_energy': c.regeneration_energy,
                'overall_score': c.overall_score,
                'toxicity': c.toxicity_LD50,
                'cost': c.cost_USD_kg,
            }
            for c in candidates
        ]
    }


@router.post("/molecular/solvent/mixture")
async def design_mixture(components: Dict[str, float]):
    designer = AmineMixtureDesigner()
    return designer.evaluate_mixture(components)


@router.post("/molecular/catalyst/design")
async def design_catalyst(req: CatalystDesignRequest):
    designer = CatalystDesigner()
    candidates = designer.design_scr_catalyst(target_conversion=req.target_conversion, operating_T=req.operating_T)
    return {
        'candidates': [
            {
                'name': c.name,
                'TOF': c.TOF,
                'selectivity': c.selectivity,
                'surface_area': c.surface_area,
                'cost': c.cost_USD_kg,
                'score': c.score,
            }
            for c in candidates
        ]
    }


@router.post("/molecular/sorbent/mercury")
async def design_hg_sorbent(target_removal: float = 0.95):
    designer = AdsorbentDesigner()
    return {'candidates': designer.design_mercury_sorbent(target_removal)}


@router.post("/doe/design")
async def create_doe(req: DoERequest):
    factors = [ExperimentalFactor(name=f['name'], low=f['low'], high=f['high'], units=f.get('units', '')) for f in req.factors]
    if req.design_type == 'full_factorial':
        design = FullFactorial(factors).design()
    elif req.design_type == 'fractional':
        design = FractionalFactorial(factors).design()
    elif req.design_type == 'CCD':
        design = CentralComposite(factors).design()
    elif req.design_type == 'BoxBehnken':
        design = BoxBehnken(factors).design()
    elif req.design_type == 'PlackettBurman':
        design = PlackettBurman(factors).design()
    else:
        raise HTTPException(400, f"Unknown design type: {req.design_type}")
    return {'design_type': req.design_type, 'n_runs': len(design), 'design': design.tolist()}


@router.post("/lims/sample/register")
async def register_sample(req: SampleRegisterRequest):
    sample = Sample(
        name=req.name, cas_number=req.cas_number, formula=req.formula, purity=req.purity,
        supplier=req.supplier, initial_quantity=req.quantity, current_quantity=req.quantity,
        units=req.units, storage_location=req.storage_location,
    )
    sample_registry.register(sample)
    return {'id': sample.id, 'name': sample.name}


@router.get("/lims/samples")
async def list_samples():
    samples = sample_registry.list_active()
    return {'samples': [{'id': s.id, 'name': s.name, 'cas': s.cas_number, 'quantity': s.current_quantity} for s in samples]}


@router.post("/safety/hazop/run")
async def run_hazop(unit_name: str = 'CO2_Absorber'):
    study = CO2AbsorptionHAZOP()
    return {
        'unit': study.node_name,
        'nodes': [
            {
                'parameter': n.parameter, 'deviation': n.deviation, 'causes': n.causes,
                'consequences': n.consequences, 'safeguards': n.safeguards, 'risk': n.risk.value,
            }
            for n in study.nodes
        ]
    }


@router.post("/discovery/hypotheses/generate")
async def generate_hypotheses(data: Dict, features: List[str]):
    generator = HypothesisGenerator(knowledge_base)
    hypotheses = generator.generate_from_data(data, features)
    return {'hypotheses': [{'id': h.id, 'statement': h.statement, 'rationale': h.rationale, 'confidence': h.confidence} for h in hypotheses]}
