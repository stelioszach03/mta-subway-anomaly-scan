from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "mta-subway-anomaly-scan"
    APP_ENV: Literal["dev", "prod"] = "dev"
    APP_VERSION: str = "0.1.0"

    # Database
    DB_URL: str = "postgresql://postgres:postgres@db:5432/mta"

    # External tokens (required)
    MAPBOX_TOKEN: str

    # Static GTFS paths (host defaults)
    MTA_GTFS_STATIC_PATH: str = (
        "/home/stelios/mta-subway-anomaly-scan/gtfs_subway/mta_gtfs_static.zip"
    )
    GTFS_STATIC_DIR: str = "/home/stelios/mta-subway-anomaly-scan/gtfs_subway"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = None  # docker-compose passes envs; local can export or use a .env loader


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
