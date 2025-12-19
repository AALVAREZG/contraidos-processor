"""Application configuration"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    app_name: str = "Contraídos Visual Analyzer"
    app_version: str = "1.0.0"
    debug: bool = True

    # API Settings
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Upload
    upload_dir: Path = Path("uploads")
    export_dir: Path = Path("exports")
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set[str] = {".xlsx", ".xls"}

    # File Retention
    file_retention_days: int = 30

    # Database (optional for MVP, using in-memory storage)
    database_url: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.upload_dir.mkdir(exist_ok=True, parents=True)
settings.export_dir.mkdir(exist_ok=True, parents=True)
