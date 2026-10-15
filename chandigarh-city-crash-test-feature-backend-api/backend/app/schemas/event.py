from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel, Field


class CivicReportCreate(BaseModel):
    category: Literal[
        "drainage_blockage",
        "waste_dumping",
        "waterlogging_onset",
        "traffic_slowdown",
        "debris_hotspot",
        "other"
    ] = Field(..., description="Classification category of civic event")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level")
    sector_id: str = Field(..., description="Target Chandigarh sector identifier, e.g. sector-17")
    location_description: str = Field(..., min_length=3, description="Specific descriptive landmark or intersection")
    reported_at: Optional[str] = Field(default=None, description="ISO timestamp")
    source: Optional[str] = Field(default="manual_entry", description="Source: citizen_app, field_marshal, voice_ai, vision_ai")
    confidence: Optional[float] = Field(default=0.90, ge=0.0, le=1.0, description="Model or reporter confidence")
    media_url: Optional[str] = Field(default=None, description="Optional photo or audio reference")


class CivicReport(CivicReportCreate):
    event_id: str
    status: Literal["unverified", "verified", "investigating", "pending_action", "resolved"] = "unverified"
    created_at: str


class CivicReportListResponse(BaseModel):
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    total_events: int
    events: List[CivicReport]
