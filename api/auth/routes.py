"""Authentication routes."""

import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status, Body
from pydantic import BaseModel, Field, ConfigDict, ValidationError
from typing_extensions import Annotated

from .service import AuthService, get_auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


class GitHubLoginResponse(BaseModel):
    """Response model for GitHub login."""
    auth_url: str
    state: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "auth_url": "https://github.com/login/oauth/authorize",
                "state": "random_state_token"
            }]
        }
    )


class GitHubCallbackResponse(BaseModel):
    """Response model for GitHub callback."""
    access_token: str
    token_type: str
    scope: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "access_token": "gho_random_token",
                "token_type": "bearer",
                "scope": "gist"
            }]
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "filename": "test.json",
                "content": "{}",
                "description": "Test gist"
            }]
        }
    )


class GistUpdate(BaseModel):
    """Schema for updating a gist."""
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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "filename": "test.json",
                "content": "{}",
                "description": "Updated test gist"
            }]
        }
    )


async def get_token(authorization: str = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme"
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )


@router.get("/login", response_model=GitHubLoginResponse)
async def github_login(
    auth_service: AuthService = Depends(get_auth_service)
) -> GitHubLoginResponse:
    """Start GitHub OAuth flow."""
    try:
        login_data = auth_service.generate_github_login_url()
        return GitHubLoginResponse(**login_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating GitHub login URL: {str(e)}"
        )


@router.get("/github", response_model=GitHubCallbackResponse)
async def github_callback(
    code: Annotated[str, Query(description="GitHub OAuth code")],
    state: Annotated[str, Query(description="CSRF state token")],
    auth_service: AuthService = Depends(get_auth_service)
) -> GitHubCallbackResponse:
    """Handle GitHub OAuth callback."""
    try:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing code parameter"
            )
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing state parameter"
            )
        
        return await auth_service.exchange_code_for_token(code, state)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error exchanging code for token: {str(e)}"
        )


@router.post("/gists", response_model=Dict)
async def create_gist(
    gist_data: dict = Body(...),
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Create a new gist."""
    try:
        # Validate content before Pydantic validation
        if not gist_data.get("content") or str(gist_data.get("content")).isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gist content cannot be empty"
            )

        # Try to parse JSON if content is meant to be JSON
        filename = gist_data.get("filename", "")
        if filename.endswith('.json'):
            try:
                json.loads(gist_data.get("content", ""))
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON content"
                )
        
        # Validate with Pydantic after basic validation
        try:
            gist = GistCreate(**gist_data)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        return await auth_service.create_gist(
            token,
            gist.filename,
            gist.content,
            gist.description
        )
    except HTTPException:
        raise
    except Exception as e:
        if "401" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create gist: {str(e)}"
        )


@router.patch("/gists/{gist_id}", response_model=Dict)
async def update_gist(
    gist_id: str,
    gist_data: dict = Body(...),
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Update an existing gist."""
    try:
        if not gist_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gist ID is required"
            )
        
        # Validate content before Pydantic validation
        if not gist_data.get("content") or str(gist_data.get("content")).isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gist content cannot be empty"
            )
        
        # Try to parse JSON if content is meant to be JSON
        filename = gist_data.get("filename", "")
        if filename.endswith('.json'):
            try:
                json.loads(gist_data.get("content", ""))
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON content"
                )
        
        # Validate with Pydantic after basic validation
        try:
            gist = GistUpdate(**gist_data)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        return await auth_service.update_gist(
            token,
            gist_id,
            gist.filename,
            gist.content,
            gist.description
        )
    except HTTPException:
        raise
    except Exception as e:
        if "401" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        if "not found" in str(e).lower() or "404" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gist not found: {gist_id}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update gist: {str(e)}"
        )


@router.get("/gists", response_model=List[Dict])
async def get_gists(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> List[Dict]:
    """Get user's gists."""
    try:
        return await auth_service.get_user_gists(token)
    except HTTPException:
        raise
    except Exception as e:
        if "401" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch gists: {str(e)}"
        )


@router.get("/gists/{gist_id}/build", response_model=Dict)
async def get_inventory(
    gist_id: str,
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Get user's DIBO inventory from gists."""
    try:
        if not gist_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gist ID is required"
            )

        return await auth_service.get_generated_build(token, gist_id)
    except HTTPException:
        raise
    except Exception as e:
        if "401" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        if "not found" in str(e).lower() or "404" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Build not found: {gist_id}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch build: {str(e)}"
        )
