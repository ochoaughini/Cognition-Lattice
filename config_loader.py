"""Load and validate environment configuration."""

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    broker_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
