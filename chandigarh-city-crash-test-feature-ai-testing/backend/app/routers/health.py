from fastapi import APIRouter
from backend.app.schemas.common import HealthCheckResponse
from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
def get_health():
    """
    Service health check endpoint.
    Confirms operational status and indicates synthetic data mode.
    """
    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        service="C3T Chandigarh City Crash Test API",
        data_status="synthetic_demo",
        message="Backend active. Decision intelligence engine online."
    )
