"""Core configuration module."""

from functools import lru_cache
from pathlib import Path
from typing import Optional, List

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API configuration settings."""

    # Project
    PROJECT_NAME: str = "DIBO API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    
    # JWT Settings
    JWT_SECRET_KEY: SecretStr = Field(
        default="your-secret-key-here",
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm to use for JWT token signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,  # 24 hours
        description="Minutes until access token expires"
    )
    
    # Data
    DATA_DIR: Path = Field(
        default="./data/indexed",
        description="Directory containing indexed game data"
    )

    @property
    def data_path(self) -> Path:
        """Get absolute path to data directory."""
        if self.DATA_DIR.is_absolute():
            return self.DATA_DIR
        return self.PROJECT_ROOT / self.DATA_DIR
    
    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="deployment environment"
    )
    
    # Testing
    TESTING: bool = Field(
        default=False,
        description="Whether the app is in testing mode"
    )
    TEST_DATA_DIR: Optional[str] = Field(
        default=None,
        description="Directory containing test data"
    )
    
    # Server Settings
    HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to"
    )
    PORT: int = Field(
        default=8000,
        description="Port to bind the server to"
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    RELOAD: bool = Field(
        default=True,
        description="Enable auto-reload on code changes"
    )
    WORKERS: int = Field(
        default=1,
        description="Number of worker processes"
    )
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: str = Field(
        default="",
        description="Comma-separated list of origins that are allowed to make cross-site HTTP requests"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Get list of allowed CORS origins."""
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # Allow credentials in CORS requests
    ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    ALLOW_METHODS: str = Field(
        default="*",
        description="HTTP methods allowed in CORS requests"
    )
    ALLOW_HEADERS: str = Field(
        default="*",
        description="HTTP headers allowed in CORS requests"
    )
    
    # GitHub OAuth - Development
    DEV_GITHUB_CLIENT_ID: str = Field(
        default="",
        description="Development GitHub OAuth client ID"
    )
    DEV_GITHUB_CLIENT_SECRET: str = Field(
        default="",
        description="Development GitHub OAuth client secret"
    )
    DEV_GITHUB_CALLBACK_URL: AnyHttpUrl = Field(
        default="http://localhost:8000/api/v1/auth/github",
        description="Development GitHub OAuth callback URL"
    )

    # GitHub OAuth - Production
    GITHUB_CLIENT_ID: str = Field(
        default="",
        description="Production GitHub OAuth client ID"
    )
    GITHUB_CLIENT_SECRET: str = Field(
        default="",
        description="Production GitHub OAuth client secret"
    )
    GITHUB_CALLBACK_URL: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Production GitHub OAuth callback URL"
    )
    
    @property
    def active_github_client_id(self) -> str:
        """Get active GitHub client ID based on environment."""
        return self.GITHUB_CLIENT_ID if self.ENVIRONMENT == "production" else self.DEV_GITHUB_CLIENT_ID
    
    @property
    def active_github_client_secret(self) -> str:
        """Get active GitHub client secret based on environment."""
        return self.GITHUB_CLIENT_SECRET if self.ENVIRONMENT == "production" else self.DEV_GITHUB_CLIENT_SECRET
    
    @property
    def active_github_callback_url(self) -> Optional[AnyHttpUrl]:
        """Get active GitHub callback URL based on environment."""
        return self.GITHUB_CALLBACK_URL if self.ENVIRONMENT == "production" else self.DEV_GITHUB_CALLBACK_URL
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        env_nested_delimiter="__",
        extra="allow"  # Allow extra fields from .env file
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
