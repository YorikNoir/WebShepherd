"""
Configuration settings for WebShepherd
Uses pydantic-settings for environment variable management
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "WebShepherd"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./webshepherd.db"

    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://192.168.2.201",
        "http://192.168.2.201:80",
        "https://yorik.space",
        "https://www.yorik.space",
        "null"  # Allow file:// protocol for local testing
    ]

    # Rate limiting
    RATE_LIMIT_PER_HOUR: int = 1000

    # Scanning limits
    MAX_HTML_SIZE_MB: int = 5
    REQUEST_TIMEOUT: int = 10
    MAX_REDIRECTS: int = 5

    # User agent
    USER_AGENT: str = "WebShepherd/1.0 (WCAG Accessibility Checker; +https://yorik.space/webshepherd)"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
