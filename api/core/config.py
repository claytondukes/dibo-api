"""Core configuration module."""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors_origin(v: str) -> AnyHttpUrl:
    """Parse CORS origin string to AnyHttpUrl."""
    # Remove quotes if present
    v = v.strip('"\'')
    return AnyHttpUrl(v)


class Settings(BaseSettings):
    """API configuration settings."""

    # Project
    PROJECT_NAME: str = "DIBO API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT token generation"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,
        description="Minutes before JWT token expires"
    )
    
    # GitHub OAuth - Production
    GITHUB_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="GitHub OAuth client ID for production"
    )
    GITHUB_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="GitHub OAuth client secret for production"
    )
    GITHUB_CALLBACK_URL: Optional[AnyHttpUrl] = Field(
        default=None,
        description="GitHub OAuth callback URL for production"
    )
    
    # GitHub OAuth - Development
    DEV_GITHUB_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="GitHub OAuth client ID for development"
    )
    DEV_GITHUB_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="GitHub OAuth client secret for development"
    )
    DEV_GITHUB_CALLBACK_URL: Optional[AnyHttpUrl] = Field(
        default="http://localhost:8000/api/v1/auth/github",
        description="GitHub OAuth callback URL for development"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = Field(
        default=[],
        description="List of origins that can access the API"
    )
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: Union[str, List[str]] = Field(
        default=["*"],
        description="HTTP methods to allow"
    )
    ALLOW_HEADERS: Union[str, List[str]] = Field(
        default=["*"],
        description="HTTP headers to allow"
    )
    
    # Rate Limiting
    RATE_LIMIT_AUTHENTICATED: int = Field(
        default=1000,
        description="Rate limit for authenticated users (requests/hour)"
    )
    RATE_LIMIT_ANONYMOUS: int = Field(
        default=60,
        description="Rate limit for anonymous users (requests/hour)"
    )
    
    # Data Files
    DATA_DIR: Path = Field(
        default=Path(__file__).parent.parent / "data",
        description="Directory containing data files"
    )
    TEST_DATA_DIR: Optional[Path] = Field(
        default=None,
        description="Directory containing test data files"
    )
    GEMS_FILE: Path = Field(
        default=None,
        description="Path to gems data file"
    )
    BUILDS_FILE: Path = Field(
        default=None,
        description="Path to builds data file"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format"
    )
    
    # Development
    TESTING: bool = False
    ENVIRONMENT: str = Field(
        default="development",
        description="deployment environment"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        env_nested_delimiter="__"
    )
    
    @property
    def active_github_client_id(self) -> str:
        """Get the active GitHub client ID based on environment."""
        if self.ENVIRONMENT == "development":
            if not self.DEV_GITHUB_CLIENT_ID:
                raise ValueError("DEV_GITHUB_CLIENT_ID must be set in development")
            return self.DEV_GITHUB_CLIENT_ID
        if not self.GITHUB_CLIENT_ID:
            raise ValueError("GITHUB_CLIENT_ID must be set in production")
        return self.GITHUB_CLIENT_ID
    
    @property
    def active_github_client_secret(self) -> str:
        """Get the active GitHub client secret based on environment."""
        if self.ENVIRONMENT == "development":
            if not self.DEV_GITHUB_CLIENT_SECRET:
                raise ValueError("DEV_GITHUB_CLIENT_SECRET must be set in development")
            return self.DEV_GITHUB_CLIENT_SECRET
        if not self.GITHUB_CLIENT_SECRET:
            raise ValueError("GITHUB_CLIENT_SECRET must be set in production")
        return self.GITHUB_CLIENT_SECRET
    
    @property
    def active_github_callback_url(self) -> AnyHttpUrl:
        """Get the active GitHub callback URL based on environment."""
        if self.ENVIRONMENT == "development":
            if not self.DEV_GITHUB_CALLBACK_URL:
                raise ValueError("DEV_GITHUB_CALLBACK_URL must be set in development")
            return self.DEV_GITHUB_CALLBACK_URL
        if not self.GITHUB_CALLBACK_URL:
            raise ValueError("GITHUB_CALLBACK_URL must be set in production")
        return self.GITHUB_CALLBACK_URL
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str, info) -> str:
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return upper_v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str, info) -> str:
        """Validate environment setting."""
        valid_envs = ["development", "staging", "production"]
        lower_v = v.lower()
        if lower_v not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {valid_envs}")
        return lower_v
    
    @field_validator("GEMS_FILE", "BUILDS_FILE", mode="before")
    @classmethod
    def set_data_files(cls, v: Optional[Path], info) -> Path:
        """Set data file paths relative to DATA_DIR."""
        if v is None:
            data_dir = info.data.get("DATA_DIR")
            if not data_dir:
                raise ValueError("DATA_DIR must be set")
            return data_dir / f"{info.field_name.lower().replace('_file', '')}.json"
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]], info) -> List[AnyHttpUrl]:
        """Process CORS origins from string or list."""
        if isinstance(v, str):
            # Split string by comma and process each origin
            return [parse_cors_origin(origin.strip()) for origin in v.split(",")]
        return [parse_cors_origin(origin) for origin in v]
    
    @field_validator("ALLOW_METHODS", "ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_list_field(cls, v: Union[str, List[str]], info) -> List[str]:
        """Parse list fields that can be either string or list."""
        if isinstance(v, str):
            # Remove quotes if present
            v = v.strip('"\'')
            if v == "*":
                return ["*"]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("Value must be a string or list")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
