"""Core configuration module."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
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
    
    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="deployment environment"
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
