"""
Contract tests: verify the v1 API behaves as documented.
These tests protect the API contract. Any change that breaks these
tests requires a MAJOR version bump.
"""

import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone

from cbms_sim.v1 import (
    SimulationEngine, SimulationRequest, SimulationResult,
    PlantProfile, ReagentFormulation, OperatingConditions,
    SimulationOptions, SimulationType, CalciumSourceType, BoilerType,
    SimulationStatus, CaptureEfficiency, KineticsResult,
    MassBalanceResult, BlockProperties, EconomicResult,
    ComplianceFlags, Sensitivities, DistributionStats,
    ParameterRegistry, ParameterSet, ParameterSetVersion,
    SimulationError, ValidationError, ConvergenceError,
    NumericalError, ParameterError, ResourceError,
    ErrorCode, ErrorContext,
    pascals_from_ppm, ppm_from_pascals, m3_per_hr_from_nm3_per_hr,
    kelvin_from_celsius, celsius_from_kelvin,
    assert_positive, assert_non_negative, assert_in_range,
)


class TestVersioning:
    """The v1 module must be importable and versioned."""
    
    def test_v1_module_exists(self):
        import cbms_sim.v1
        assert cbms_sim.v1 is not None
    
    def test_v1_has_version(self):
        from cbms_sim.v1 import __version__, __api_version__
        assert __version__ == "1.0.0"
        assert __api_version__ == "v1"


class TestUnitConversions:
    """Test unit conversion helpers."""
    
    def test_temperature_conversions(self):
        assert kelvin_from_celsius(25.0) == 298.15
        assert celsius_from_kelvin(298.15) == 25.0
        with pytest.raises(ValueError):
            celsius_from_kelvin(-5.0)
            
    def test_pressure_ppm_conversions(self):
        pa = pascals_from_ppm(1000.0, 64.07)
        assert abs(pa - 101.325) < 1e-3
        ppm = ppm_from_pascals(pa)
        assert abs(ppm - 1000.0) < 1e-3
        
        with pytest.raises(ValueError):
            pascals_from_ppm(-10.0, 44.0)
        with pytest.raises(ValueError):
            ppm_from_pascals(-10.0)
            
    def test_flow_conversions(self):
        flow = m3_per_hr_from_nm3_per_hr(10000.0, 313.15)
        # Flow actual is higher than normal at 40°C
        assert flow < 10000.0  # since STANDARD_TEMP_K is 298.15, 10000 * 298.15/313.15 < 10000
        
    def test_assert_helpers(self):
        assert_positive(5.0)
        assert_non_negative(0.0)
        assert_in_range(5.0, 0.0, 10.0)
        
        with pytest.raises(ValueError):
            assert_positive(-1.0)
        with pytest.raises(ValueError):
            assert_non_negative(-0.5)
        with pytest.raises(ValueError):
            assert_in_range(11.0, 0.0, 10.0)


class TestParameterRegistryContract:
    """Test registry and version loading."""
    
    def test_load_registry_by_version(self):
        registry = ParameterRegistry.from_version("v2026.1")
        assert registry.version == "2026.1"
        k_cat = registry.get("kinetics.k_cat")
        assert k_cat["value"] == 1000000.0
        assert registry.get_value("kinetics.k_cat") == 1000000.0
        
        paths = registry.list_parameters("kinetics")
        assert "kinetics.k_cat" in paths
        
        with pytest.raises(ParameterError):
            registry.get("invalid.param")


@pytest.fixture
def sample_request():
    plant = PlantProfile(
        id=uuid4(),
        name="Mumbai Power Plant",
        location="Maharashtra",
        boiler_type=BoilerType.PULVERIZED_COAL,
        exhaust_flow_nm3_hr=Decimal("10000.0"),
        baseline_temperature_c=Decimal("150.0"),
        co2_vol_pct=Decimal("14.0"),
        so2_mg_per_nm3=Decimal("1200.0"),
        nox_mg_per_nm3=Decimal("450.0"),
        fly_ash_g_per_nm3=Decimal("45.0"),
        heavy_metal_profile=[{"element": "Hg", "conc_ug_per_nm3": 5.0}],
        operating_hours_per_year=8000
    )
    
    reagent = ReagentFormulation(
        id=uuid4(),
        name="Chitosan Matrix 3.0",
        chitosan_wt_pct=Decimal("3.0"),
        ca_source_type=CalciumSourceType.LIME,
        ca_wt_pct=Decimal("3.5"),
        enzyme_mg_per_l=Decimal("12.0")
    )
    
    conditions = OperatingConditions(
        reactor_temp_c=Decimal("40.0"),
        pH_initial=Decimal("8.5"),
        liquid_to_gas_ratio=Decimal("8.5"),
        residence_time_s=Decimal("27.0")
    )
    
    return SimulationRequest(
        request_id=uuid4(),
        org_id=uuid4(),
        user_id=uuid4(),
        plant=plant,
        reagent=reagent,
        conditions=conditions,
        options=SimulationOptions(
            simulation_type=SimulationType.BASELINE,
            random_seed=42
        ),
        submitted_at=datetime.now(timezone.utc)
    )


class TestSimulationEngineContract:
    """Test running simulations via public interface."""
        
    def test_baseline_solve(self, sample_request):
        engine = SimulationEngine(parameter_set="v2026.1")
        engine.warmup()
        
        result = engine.run(sample_request)
        assert isinstance(result, SimulationResult)
        assert result.is_successful
        assert result.kinetics is not None
        assert result.mass_balance is not None
        assert result.block is not None
        assert result.economic is not None
        
        assert result.kinetics.capture.co2_pct > 0.0
        assert result.mass_balance.caco3_output_kg_hr > 0.0
        assert result.block.strength_mpa > 0.0
        assert result.economic.npv_10yr_inr != 0.0
        
    def test_monte_carlo_solve(self, sample_request):
        sample_request = sample_request.model_copy(update={
            "options": SimulationOptions(
                simulation_type=SimulationType.MONTE_CARLO,
                n_mc_samples=100,
                random_seed=42
            )
        })
        
        engine = SimulationEngine(parameter_set="v2026.1")
        result = engine.run(sample_request)
        
        assert result.is_successful
        assert result.capture_distribution is not None
        assert result.capture_distribution.n_samples == 100
        assert result.npv_distribution is not None
        assert result.payback_distribution is not None
        
    def test_validation_exception_on_bad_inputs(self, sample_request):
        # Trigger Pydantic error
        with pytest.raises(Exception):
            PlantProfile(
                id=uuid4(),
                name="",
                location="Maharashtra",
                boiler_type=BoilerType.PULVERIZED_COAL,
                exhaust_flow_nm3_hr=Decimal("-10.0"),  # Invalid
                baseline_temperature_c=Decimal("150.0"),
                co2_vol_pct=Decimal("14.0"),
                so2_mg_per_nm3=Decimal("1200.0"),
                nox_mg_per_nm3=Decimal("450.0"),
                fly_ash_g_per_nm3=Decimal("45.0")
            )
            
        # Trigger validation error in request
        bad_request = sample_request.model_copy(update={
            "plant": sample_request.plant.model_copy(update={
                "exhaust_flow_nm3_hr": Decimal("600000.0")  # > 500,000 threshold
            })
        })
        engine = SimulationEngine(parameter_set="v2026.1")
        with pytest.raises(ValidationError):
            engine.run(bad_request)


class TestValidators:
    """Test v1 validators helper functions."""

    def test_validators_success(self, sample_request):
        from cbms_sim.v1.validators import (
            validate_simulation_request, validate_plant_profile,
            validate_reagent_formulation, validate_operating_conditions
        )
        
        # Object validation
        assert validate_simulation_request(sample_request) == sample_request
        assert validate_plant_profile(sample_request.plant) == sample_request.plant
        assert validate_reagent_formulation(sample_request.reagent) == sample_request.reagent
        assert validate_operating_conditions(sample_request.conditions) == sample_request.conditions

        # Dict validation
        plant_dict = sample_request.plant.model_dump()
        reagent_dict = sample_request.reagent.model_dump()
        conds_dict = sample_request.conditions.model_dump()
        req_dict = sample_request.model_dump()
        
        assert validate_plant_profile(plant_dict).id == sample_request.plant.id
        assert validate_reagent_formulation(reagent_dict).id == sample_request.reagent.id
        assert validate_operating_conditions(conds_dict).pH_initial == sample_request.conditions.pH_initial
        assert validate_simulation_request(req_dict).request_id == sample_request.request_id

    def test_validators_failure(self):
        from cbms_sim.v1.validators import (
            validate_simulation_request, validate_plant_profile,
            validate_reagent_formulation, validate_operating_conditions
        )
        
        with pytest.raises(ValidationError):
            validate_plant_profile("not-a-dict")
        with pytest.raises(ValidationError):
            validate_reagent_formulation(123)
        with pytest.raises(ValidationError):
            validate_operating_conditions([])
        with pytest.raises(ValidationError):
            validate_simulation_request(None)


class TestExceptions:
    """Test custom exception serialization and formatting."""
    
    def test_simulation_error_properties(self):
        from cbms_sim.v1.exceptions import ErrorContext, ErrorCode
        
        context = ErrorContext(
            request_id="req-123",
            run_id="run-456",
            parameter_set_version="v2026.1",
            code_version="1.0.0",
            stage="kinetics",
            extra={"test": "data"}
        )
        
        exc = SimulationError("Test message", code=ErrorCode.NUMERICAL_INSTABILITY, context=context)
        assert exc.message == "Test message"
        assert exc.code == ErrorCode.NUMERICAL_INSTABILITY
        assert "stage=kinetics" in str(exc)
        assert "run_id=run-456" in str(exc)
        
        d = exc.to_dict()
        assert d["error_type"] == "SimulationError"
        assert d["code"] == "NUMERICAL_INSTABILITY"
        assert d["context"]["request_id"] == "req-123"
        assert d["context"]["test"] == "data"
        
    def test_other_exceptions(self):
        c_exc = ConvergenceError("Convergence fail", nfev=42)
        assert c_exc.code == ErrorCode.SOLVER_DIVERGENCE
        assert c_exc.context.extra["nfev"] == 42
        
        p_exc = ParameterError("Param fail", parameter="k_cat")
        assert p_exc.context.extra["parameter"] == "k_cat"
        
        r_exc = ResourceError("Out of memory", code=ErrorCode.OUT_OF_MEMORY)
        assert r_exc.code == ErrorCode.OUT_OF_MEMORY

