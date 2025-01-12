"""Authentication schemas."""

from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json


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
    filename: str = Field(
        description="Name of the gist file",
        min_length=1,
        max_length=255,
        pattern=r"^[\w\-. ]+$"
    )
    content: str = Field(
        description="Content of the gist",
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "filename": "test.json",
                "content": "{}"
            }]
        }
    }


class GistCreate(BaseModel):
    """Schema for creating a gist."""
    filename: str = Field(
        description="Name of the gist file",
        min_length=1,
        max_length=255,
        pattern=r"^[\w\-. ]+$"
    )
    content: str = Field(
        description="Content of the gist",
        min_length=1
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional gist description",
        max_length=1000
    )

    @field_validator("content")
    def validate_json_content(cls, v, values):
        """Validate that content is valid JSON if filename ends with .json."""
        if "filename" in values and values["filename"].endswith(".json"):
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Content must be valid JSON for .json files")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "filename": "test.json",
                "content": "{}",
                "description": "Test gist"
            }]
        }
    }


class GistUpdate(GistCreate):
    """Schema for updating a gist."""
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "filename": "test.json",
                "content": "{}",
                "description": "Updated test gist"
            }]
        }
    }


class GistResponse(BaseModel):
    """Response model for gist operations."""
    id: str = Field(description="Gist ID")
    html_url: str = Field(description="Gist URL")
    files: Dict[str, GistFile] = Field(description="Gist files")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "abc123",
                "html_url": "https://gist.github.com/user/abc123",
                "files": {
                    "test.json": {
                        "filename": "test.json",
                        "content": "{}"
                    }
                },
                "created_at": "2025-01-11T19:38:01-05:00",
                "updated_at": "2025-01-11T19:38:01-05:00"
            }]
        }
    }


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
