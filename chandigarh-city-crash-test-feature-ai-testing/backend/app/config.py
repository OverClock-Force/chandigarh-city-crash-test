import os
from pathlib import Path


class Settings:
    PROJECT_NAME: str = "Chandigarh City Crash Test (C3T) API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATA_STATUS: str = "synthetic_demo"
    SCORE_LABEL: str = "Unvalidated demo index (0-100)"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",  # permissive for hackathon multi-device and demo testing
    ]


settings = Settings()
