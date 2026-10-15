from fastapi import APIRouter
from risk_engine.models import ScenarioInput, RiskAssessmentResult
from risk_engine.calculator import calculate_scenario_risk
from backend.app.storage.store import store

router = APIRouter(prefix="/api/stress-test", tags=["Stress Test Engine"])


@router.post("", response_model=RiskAssessmentResult)
def run_stress_test(scenario: ScenarioInput):
    """
    Validate a scenario, run the cross-domain risk engine and cascade generator,
    and return sector-level risk breakdowns and causal links.
    """
    sectors_data = store.get_sectors()
    result = calculate_scenario_risk(scenario, sectors_data)
    return result
