from typing import Optional, Literal
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    service: str = "C3T Chandigarh City Crash Test API"
    data_status: Literal["synthetic_demo"] = "synthetic_demo"
    message: str = "Service operational. All outputs are unvalidated demo calculations."
