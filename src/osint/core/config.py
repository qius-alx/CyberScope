# src/osint/core/config.py
import logging
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Application settings are defined here.
    Pydantic will automatically load values from environment variables
    or a .env file.
    """
    # Core settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    output_dir: str = Field("results", env="OUTPUT_DIR")

    # HTTP settings
    http_timeout: int = Field(30, env="HTTP_TIMEOUT")
    http_retries: int = Field(3, env="HTTP_RETRIES")
    http_proxy: Optional[str] = Field(None, env="HTTP_PROXY")
    tor_proxy: Optional[str] = Field("socks5h://localhost:9050", env="TOR_PROXY")
    user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        env="USER_AGENT"
    )

    # Concurrency
    threads: int = Field(10, env="THREADS")

    # API Keys (optional)
    shodan_api_key: Optional[str] = Field(None, env="SHODAN_API_KEY")
    hibp_api_key: Optional[str] = Field(None, env="HIBP_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings.
    """
    return Settings()


# Initialize settings
settings = get_settings()
