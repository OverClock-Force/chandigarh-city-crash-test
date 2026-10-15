from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import sys
from pathlib import Path

# Ensure root workspace is in sys.path so risk_engine is importable
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.config import settings
from backend.app.routers import (
    health_router,
    sectors_router,
    events_router,
    stress_test_router,
    optimize_router,
    scenarios_router,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Chandigarh City Crash Test (C3T) Backend Service.\n\n"
        "A preventive urban decision intelligence API modeling cascading risks across "
        "waste, drainage, environmental heat, and traffic infrastructure under stress scenarios.\n\n"
        "**Golden Rule**: Every simulated result is labeled illustrative / synthetic_demo. "
        "Never presented as an uncalibrated real forecast."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Validation Exception Handler for frontend-friendly error format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error.get("loc", []) if loc != "body"])
        errors.append({
            "field": field,
            "message": error.get("msg"),
            "type": error.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": "One or more scenario input constraints were violated.",
            "field_errors": errors,
            "rules": {
                "rainfall_mm": "Must be between 15 and 100 mm",
                "temperature_c": "Must be between 32 and 43 °C",
                "debris_level": "Allowed: 'normal', 'high', 'extreme'",
                "drain_condition": "Allowed: 'good', 'partial_blockage', 'critical'",
                "traffic_level": "Allowed: 'normal', 'peak'"
            }
        }
    )

# Register routers
app.include_router(health_router)
app.include_router(sectors_router)
app.include_router(events_router)
app.include_router(stress_test_router)
app.include_router(optimize_router)
app.include_router(scenarios_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "Chandigarh City Crash Test (C3T) API",
        "version": settings.VERSION,
        "status": "online",
        "data_status": "synthetic_demo",
        "score_label": "Unvalidated demo index (0-100)",
        "endpoints": {
            "health": "/health",
            "sectors": "/api/sectors",
            "events": "/api/events",
            "stress_test": "/api/stress-test",
            "optimize": "/api/optimize",
            "scenarios": "/api/scenarios",
            "documentation": "/docs"
        },
        "team_lead": "Aman Gupta (Backend & Data Lead)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
