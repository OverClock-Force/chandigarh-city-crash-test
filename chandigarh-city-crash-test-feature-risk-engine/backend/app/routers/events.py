from typing import Optional
from fastapi import APIRouter, Query, status
from backend.app.schemas.event import CivicReportCreate, CivicReport, CivicReportListResponse
from backend.app.storage.store import store

router = APIRouter(prefix="/api/events", tags=["Civic Events"])


@router.get("", response_model=CivicReportListResponse)
def list_events(sector_id: Optional[str] = Query(None, description="Optional sector filter e.g. sector-17")):
    """
    List civic reports and field observations.
    Optionally filter by sector_id.
    """
    events = store.get_events(sector_id=sector_id)
    return CivicReportListResponse(
        data_status="synthetic_demo",
        total_events=len(events),
        events=events
    )


@router.post("", response_model=CivicReport, status_code=status.HTTP_201_CREATED)
def submit_event(report: CivicReportCreate):
    """
    Submit a citizen or field civic event report (e.g. gully blockage, illegal waste, pooling).
    Stores event for downstream risk inference.
    """
    return store.add_event(report)
