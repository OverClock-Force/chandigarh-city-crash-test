from .health import router as health_router
from .sectors import router as sectors_router
from .events import router as events_router
from .stress_test import router as stress_test_router
from .optimize import router as optimize_router
from .scenarios import router as scenarios_router

__all__ = [
    "health_router",
    "sectors_router",
    "events_router",
    "stress_test_router",
    "optimize_router",
    "scenarios_router",
]
