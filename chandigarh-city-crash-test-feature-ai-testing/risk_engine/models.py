from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ResourcesInput(BaseModel):
    maintenance_teams: int = Field(default=4, ge=0, description="Available municipal maintenance teams")
    pumping_units: int = Field(default=2, ge=0, description="Available mobile pumping units")
    budget_inr: float = Field(default=350000.0, ge=0.0, description="Available emergency operational budget in INR")


class ScenarioInput(BaseModel):
    scenario_id: Optional[str] = Field(default=None, description="Optional unique identifier for scenario")
    title: Optional[str] = Field(default="Custom Scenario", description="Human-readable title")
    rainfall_mm: float = Field(
        ...,
        ge=15.0,
        le=100.0,
        description="Total rainfall in mm, strictly enforced between 15 and 100"
    )
    rainfall_duration_hours: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=48.0,
        description="Optional duration of rain event in hours"
    )
    debris_level: Literal["normal", "high", "extreme"] = Field(
        ...,
        description="Debris/waste accumulation level"
    )
    drain_condition: Literal["good", "partial_blockage", "critical"] = Field(
        ...,
        description="Underlying drain infrastructure status"
    )
    traffic_level: Literal["normal", "peak"] = Field(
        ...,
        description="City road network traffic condition"
    )
    temperature_c: float = Field(
        ...,
        ge=32.0,
        le=43.0,
        description="Ambient temperature in Celsius (treated as heat-stress pathway; does not raise flood risk)"
    )
    resources: ResourcesInput = Field(
        default_factory=ResourcesInput,
        description="Allocated resources for intervention testing"
    )


class ComponentScores(BaseModel):
    drainage_stress: float = Field(..., ge=0.0, le=100.0)
    waterlogging: float = Field(..., ge=0.0, le=100.0)
    road_traffic: float = Field(..., ge=0.0, le=100.0)
    emergency_access: float = Field(..., ge=0.0, le=100.0)
    heat_stress_context: float = Field(..., ge=0.0, le=100.0)


class SectorRiskScore(BaseModel):
    sector_id: str
    sector_name: Optional[str] = None
    score: float = Field(..., ge=0.0, le=100.0)
    category: Optional[str] = "moderate"  # low, moderate, high, severe
    main_factors: List[str]


class CascadeLink(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    evidence_status: Literal["modeled", "hypothetical"]
    intensity: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    description: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class RiskAssessmentResult(BaseModel):
    scenario_id: str
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    score_label: Literal["Unvalidated demo index (0-100)"] = "Unvalidated demo index (0-100)"
    overall_score: float = Field(..., ge=0.0, le=100.0)
    components: ComponentScores
    sectors: List[SectorRiskScore]
    cascade: List[CascadeLink]
    assumptions: List[str]


class SectorData(BaseModel):
    sector_id: str
    name: str
    elevation_factor: float = Field(default=0.5, ge=0.0, le=1.0)  # 1.0 = low-lying depression
    drain_vulnerability: float = Field(default=0.5, ge=0.0, le=1.0)  # 1.0 = high vulnerability
    road_exposure: float = Field(default=0.5, ge=0.0, le=1.0)  # 1.0 = arterial/junction exposure
    waste_pressure: float = Field(default=0.5, ge=0.0, le=1.0)  # 1.0 = commercial/market waste
    green_cover_factor: float = Field(default=0.5, ge=0.0, le=1.0)  # 1.0 = high shade/cooling
    is_historic_hotspot: bool = False
    critical_infrastructure: List[str] = []
    coordinates: Optional[Dict[str, float]] = None


class InterventionOption(BaseModel):
    action_id: str
    name: str
    description: str
    maintenance_teams_needed: int
    pumping_units_needed: int
    cost_inr: float
    operational_burden_score: float = Field(default=10.0, ge=0.0, le=100.0)
    targeted_sectors: Optional[List[str]] = None


class InterventionEvaluation(BaseModel):
    action_id: str
    name: str
    is_feasible: bool
    feasibility_reasons: List[str]
    resources_used: Dict[str, Any]
    resources_remaining: Dict[str, Any]
    baseline_risk_score: float
    modeled_risk_score: float
    risk_reduction: float
    utility_score: float
    assumptions: List[str]
    components: ComponentScores


class OptimizationResult(BaseModel):
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    score_label: Literal["Unvalidated demo index (0-100)"] = "Unvalidated demo index (0-100)"
    baseline_score: float
    recommended_action: InterventionEvaluation
    all_evaluations: List[InterventionEvaluation]
    comparison_summary: str
