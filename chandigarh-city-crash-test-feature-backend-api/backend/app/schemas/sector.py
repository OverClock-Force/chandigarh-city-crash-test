from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class SectorDetail(BaseModel):
    sector_id: str
    name: str
    elevation_factor: float
    drain_vulnerability: float
    road_exposure: float
    waste_pressure: float
    green_cover_factor: float
    is_historic_hotspot: bool
    critical_infrastructure: List[str]
    coordinates: Optional[Dict[str, float]] = None


class SectorListResponse(BaseModel):
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    score_label: Literal["Unvalidated demo index (0-100)"] = "Unvalidated demo index (0-100)"
    total_sectors: int
    sectors: List[SectorDetail]
    geojson: Optional[Dict[str, Any]] = None
