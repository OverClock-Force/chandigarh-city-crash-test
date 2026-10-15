from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from risk_engine.models import ScenarioInput, ResourcesInput


class ScenarioSaveRequest(ScenarioInput):
    pass


class ScenarioSavedItem(ScenarioInput):
    scenario_id: str
    created_at: str


class ScenarioListResponse(BaseModel):
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    total_scenarios: int
    scenarios: List[ScenarioSavedItem]
