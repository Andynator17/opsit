"""Application configuration"""
from typing import List
import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    PROJECT_NAME: str = "OpsIT"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    # Stored as a raw string and parsed lazily. We don't type this as
    # List[str] because pydantic-settings v2 tries to JSON-decode such
    # env values BEFORE field validators run, which crashes on empty
    # strings. Use the `cors_origins` property below to get the parsed
    # list.
    BACKEND_CORS_ORIGINS: str = ""

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILES_PER_UPLOAD: int = 5

    # First Admin User (for seeding)
    FIRST_ADMIN_EMAIL: str = "admin@opsit.local"
    FIRST_ADMIN_PASSWORD: str = "Admin123!"

    @property
    def cors_origins(self) -> List[str]:
        """Parse BACKEND_CORS_ORIGINS into a list of origins.

        Accepts:
          - empty string  -> []
          - JSON array    -> ["https://a", "https://b"]
          - comma list    -> "https://a,https://b"
        """
        v = (self.BACKEND_CORS_ORIGINS or "").strip()
        if not v:
            return []
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
            return [str(parsed)]
        except json.JSONDecodeError:
            return [origin.strip() for origin in v.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


settings = get_settings()
