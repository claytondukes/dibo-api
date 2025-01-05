"""Authentication schemas."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class GitHubLoginResponse(BaseModel):
    """Response model for GitHub login."""
    auth_url: str = Field(description="GitHub OAuth URL")
    state: str = Field(description="CSRF state token")


class GitHubCallbackResponse(BaseModel):
    """Response model for GitHub callback."""
    access_token: str = Field(description="GitHub access token")
    token_type: str = Field(description="Token type (usually 'bearer')")
    scope: str = Field(description="Token scopes")


class GistFile(BaseModel):
    """Schema for a gist file."""
    filename: str = Field(examples=["test.json"])
    content: str = Field(examples=['{"test": "data"}'])


class GistCreate(BaseModel):
    """Schema for creating a gist."""
    filename: str = Field(examples=["test.json"])
    content: str = Field(examples=['{"test": "data"}'])
    description: Optional[str] = Field(default=None, examples=["Test gist"])


class GistUpdate(BaseModel):
    """Schema for updating a gist."""
    filename: str = Field(examples=["test.json"])
    content: str = Field(examples=['{"test": "data"}'])
    description: Optional[str] = Field(default=None, examples=["Updated test gist"])


class GistResponse(BaseModel):
    """Response model for gist operations."""
    id: str = Field(description="Gist ID")
    html_url: str = Field(description="Gist URL")
    files: Dict[str, GistFile] = Field(description="Gist files")


class BuildCreate(BaseModel):
    """Schema for creating a build."""
    name: str = Field(examples=["Test Build"])
    class_name: str = Field(alias="class", examples=["Barbarian"])
    type: str = Field(examples=["PvE"])
    focus: str = Field(examples=["Farming"])
    gear: Dict = Field(default_factory=dict)
    skills: Dict = Field(default_factory=dict)
    paragon: Dict = Field(default_factory=dict)
    codex: Dict = Field(default_factory=dict)
    inventory_based: bool = Field(default=True)
