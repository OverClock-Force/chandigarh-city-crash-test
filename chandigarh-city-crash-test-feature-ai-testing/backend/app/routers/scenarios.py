from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.scenario import ScenarioListResponse, ScenarioSavedItem, ScenarioSaveRequest
from backend.app.storage.store import store

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])


@router.get("", response_model=ScenarioListResponse)
def list_scenarios():
    """
    List benchmark and custom saved stress scenarios.
    """
    scenarios = store.get_scenarios()
    return ScenarioListResponse(
        data_status="synthetic_demo",
        total_scenarios=len(scenarios),
        scenarios=scenarios
    )


@router.post("", response_model=ScenarioSavedItem, status_code=status.HTTP_201_CREATED)
def save_scenario(scenario: ScenarioSaveRequest):
    """
    Save or update a scenario configuration for repeatable comparison in the Stress-Test Lab.
    """
    return store.save_scenario(scenario)


@router.get("/{scenario_id}", response_model=ScenarioSavedItem)
def get_scenario(scenario_id: str):
    """
    Retrieve details for a specific scenario by ID.
    """
    scen = store.get_scenario_by_id(scenario_id)
    if not scen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' not found."
        )
    return scen
