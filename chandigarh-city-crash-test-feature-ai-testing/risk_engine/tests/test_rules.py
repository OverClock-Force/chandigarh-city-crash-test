import pytest
from pydantic import ValidationError
from risk_engine.models import ScenarioInput, ResourcesInput, SectorData
from risk_engine.calculator import calculate_scenario_risk, compute_component_scores
from risk_engine.optimizer import evaluate_interventions

SAMPLE_SECTORS = [
    SectorData(
        sector_id="sector-17",
        name="Sector 17 (City Center)",
        elevation_factor=0.8,
        drain_vulnerability=0.7,
        road_exposure=0.9,
        waste_pressure=0.7,
        green_cover_factor=0.3,
        is_historic_hotspot=True,
    ),
    SectorData(
        sector_id="sector-35",
        name="Sector 35 (Commercial & Hotel Hub)",
        elevation_factor=0.7,
        drain_vulnerability=0.6,
        road_exposure=0.8,
        waste_pressure=0.6,
        green_cover_factor=0.4,
        is_historic_hotspot=True,
    ),
    SectorData(
        sector_id="sector-8",
        name="Sector 8 (Residential North)",
        elevation_factor=0.3,
        drain_vulnerability=0.3,
        road_exposure=0.3,
        waste_pressure=0.2,
        green_cover_factor=0.8,
        is_historic_hotspot=False,
    ),
]


def test_input_validation_bounds():
    # Valid scenario
    valid = ScenarioInput(
        rainfall_mm=60.0,
        debris_level="high",
        drain_condition="partial_blockage",
        traffic_level="peak",
        temperature_c=38.0,
    )
    assert valid.rainfall_mm == 60.0

    # Below minimum rainfall (15mm)
    with pytest.raises(ValidationError):
        ScenarioInput(
            rainfall_mm=10.0,
            debris_level="high",
            drain_condition="partial_blockage",
            traffic_level="peak",
            temperature_c=38.0,
        )

    # Above maximum rainfall (100mm)
    with pytest.raises(ValidationError):
        ScenarioInput(
            rainfall_mm=110.0,
            debris_level="high",
            drain_condition="partial_blockage",
            traffic_level="peak",
            temperature_c=38.0,
        )

    # Temperature below 32C
    with pytest.raises(ValidationError):
        ScenarioInput(
            rainfall_mm=60.0,
            debris_level="high",
            drain_condition="partial_blockage",
            traffic_level="peak",
            temperature_c=25.0,
        )


def test_direction_of_change_rainfall():
    low_rain = ScenarioInput(
        rainfall_mm=25.0,
        debris_level="normal",
        drain_condition="good",
        traffic_level="normal",
        temperature_c=35.0,
    )
    high_rain = ScenarioInput(
        rainfall_mm=85.0,
        debris_level="normal",
        drain_condition="good",
        traffic_level="normal",
        temperature_c=35.0,
    )
    res_low = compute_component_scores(low_rain)
    res_high = compute_component_scores(high_rain)

    assert res_high.drainage_stress > res_low.drainage_stress
    assert res_high.waterlogging > res_low.waterlogging


def test_temperature_independence_from_flood_risk():
    """
    CRITICAL SPECIFICATION: Temperature is treated as a separate heat-stress pathway;
    it does not raise flood risk.
    """
    scen_32c = ScenarioInput(
        rainfall_mm=50.0,
        debris_level="normal",
        drain_condition="good",
        traffic_level="normal",
        temperature_c=32.0,
    )
    scen_43c = ScenarioInput(
        rainfall_mm=50.0,
        debris_level="normal",
        drain_condition="good",
        traffic_level="normal",
        temperature_c=43.0,
    )

    res_32 = compute_component_scores(scen_32c)
    res_43 = compute_component_scores(scen_43c)

    # Flood-related components must remain completely identical
    assert res_32.drainage_stress == res_43.drainage_stress
    assert res_32.waterlogging == res_43.waterlogging
    assert res_32.road_traffic == res_43.road_traffic
    assert res_32.emergency_access == res_43.emergency_access

    # Only heat stress context should increase
    assert res_43.heat_stress_context > res_32.heat_stress_context


def test_optimizer_resource_limits():
    # Scenario with 0 budget and 0 teams
    starved_resources = ScenarioInput(
        rainfall_mm=70.0,
        debris_level="high",
        drain_condition="critical",
        traffic_level="peak",
        temperature_c=36.0,
        resources=ResourcesInput(maintenance_teams=0, pumping_units=0, budget_inr=0.0)
    )

    opt_result = evaluate_interventions(starved_resources, SAMPLE_SECTORS)

    # All non-baseline interventions must be infeasible
    for ev in opt_result.all_evaluations:
        if ev.action_id != "do_nothing":
            assert ev.is_feasible is False
            assert len(ev.feasibility_reasons) > 0

    assert opt_result.recommended_action.action_id == "do_nothing"


def test_optimizer_selects_beneficial_action():
    # Scenario with ample resources
    rich_scenario = ScenarioInput(
        rainfall_mm=75.0,
        debris_level="extreme",
        drain_condition="critical",
        traffic_level="peak",
        temperature_c=37.0,
        resources=ResourcesInput(maintenance_teams=6, pumping_units=4, budget_inr=500000.0)
    )

    opt_result = evaluate_interventions(rich_scenario, SAMPLE_SECTORS)
    assert opt_result.recommended_action.action_id != "do_nothing"
    assert opt_result.recommended_action.risk_reduction > 0
    assert opt_result.recommended_action.is_feasible is True
