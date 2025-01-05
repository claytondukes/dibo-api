"""Authentication models."""

from pydantic import BaseModel, EmailStr, HttpUrl, Field


class GitHubUser(BaseModel):
    """GitHub user model."""
    id: int
    login: str
    name: str | None = None
    email: EmailStr | None = None
    avatar_url: HttpUrl | None = None


class OAuthCallback(BaseModel):
    """OAuth callback parameters."""
    code: str = Field(description="OAuth code from GitHub")
    state: str = Field(description="State parameter for CSRF protection")


class UserProfile(BaseModel):
    """User profile model."""
    id: str
    username: str
    name: str | None = None
    email: EmailStr | None = None
    avatar_url: HttpUrl | None = None
