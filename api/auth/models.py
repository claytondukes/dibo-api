"""Authentication models."""

from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, ConfigDict


class GitHubUser(BaseModel):
    """GitHub user profile data."""
    
    model_config = ConfigDict(extra='allow')  # Allow extra fields from GitHub API
    
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl] = None


class UserProfile(BaseModel):
    """User profile response model."""
    
    id: str
    username: str
    avatar_url: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class OAuthState(BaseModel):
    """OAuth state data for CSRF protection."""
    
    state: str
    redirect_uri: Optional[HttpUrl] = None


class OAuthCallback(BaseModel):
    """OAuth callback request data."""
    
    code: str
    state: str
