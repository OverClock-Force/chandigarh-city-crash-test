from fastapi import APIRouter
from backend.app.schemas.sector import SectorListResponse, SectorDetail
from backend.app.storage.store import store

router = APIRouter(prefix="/api/sectors", tags=["Sectors"])


@router.get("", response_model=SectorListResponse)
def get_sectors():
    """
    Returns Chandigarh sectors metadata and GeoJSON boundaries.
    All data is labeled as synthetic / unvalidated demo data.
    """
    raw_sectors = store.get_sectors_raw()
    geojson_data = store.get_geojson()

    return SectorListResponse(
        data_status="synthetic_demo",
        score_label="Unvalidated demo index (0-100)",
        total_sectors=len(raw_sectors),
        sectors=[SectorDetail(**s) for s in raw_sectors],
        geojson=geojson_data
    )
