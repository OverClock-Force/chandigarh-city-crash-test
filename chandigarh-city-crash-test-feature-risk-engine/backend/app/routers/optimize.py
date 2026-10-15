from fastapi import APIRouter
from risk_engine.models import ScenarioInput, OptimizationResult
from risk_engine.optimizer import optimize_interventions
from backend.app.storage.store import store

router = APIRouter(prefix="/api/optimize", tags=["Intervention Optimizer"])


@router.post("", response_model=OptimizationResult)
def run_optimization(scenario: ScenarioInput):
    """
    Compare candidate interventions under resource limits using the same risk engine.
    Compares against unmitigated 'Do Nothing' baseline and returns the intervention
    with the highest feasible constrained utility.
    """
    sectors_data = store.get_sectors()
    result = optimize_interventions(scenario, sectors_data)
    return result
