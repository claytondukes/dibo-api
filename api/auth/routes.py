"""Authentication routes."""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status, Body
from pydantic import BaseModel
import json

from api.core.config import Settings, get_settings
from api.auth.service import AuthService, get_auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


class GitHubLoginResponse(BaseModel):
    """Response model for GitHub login."""
    auth_url: str
    state: str


class GitHubCallbackResponse(BaseModel):
    """Response model for GitHub callback."""
    access_token: str
    token_type: str
    scope: str


class GistCreate(BaseModel):
    """Schema for creating a gist."""
    filename: str
    content: str
    description: Optional[str] = None


class GistUpdate(BaseModel):
    """Schema for updating a gist."""
    filename: str
    content: str
    description: Optional[str] = None


def get_token(authorization: str = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return authorization.split(" ")[1]


@router.get("/login", response_model=GitHubLoginResponse)
async def github_login(
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Get GitHub login URL."""
    return auth_service.generate_github_login_url()


@router.get("/github", response_model=GitHubCallbackResponse)
async def github_callback(
    code: str = Query(..., description="GitHub OAuth code"),
    state: str = Query(..., description="CSRF state token"),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Handle GitHub OAuth callback."""
    try:
        return await auth_service.exchange_code_for_token(code, state)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/gists")
async def get_gists(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> List[Dict]:
    """Get user's gists."""
    try:
        return await auth_service.get_user_gists(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/gists", status_code=status.HTTP_201_CREATED)
async def create_gist(
    gist: GistCreate,
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Create a new gist."""
    try:
        return await auth_service.create_gist(
            token,
            gist.filename,
            gist.content,
            gist.description
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to create gist"
        )


@router.patch("/gists/{gist_id}")
async def update_gist(
    gist_id: str,
    gist: GistUpdate,
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Update a gist."""
    try:
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
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gist not found"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to update gist"
        )


@router.get("/inventory")
async def get_inventory(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """Get user's DIBO inventory from gists."""
    try:
        gists = await auth_service.get_user_gists(token)
        
        # Find DIBO inventory gist
        inventory_gist = next(
            (g for g in gists if g["description"] == "DIBO Inventory"),
            None
        )
        
        # Return empty inventory if no gist found
        if not inventory_gist:
            return {
                "profile": {"version": "1.0", "name": None, "class": None},
                "gems": {"version": "1.0", "gems": []},
                "sets": {"version": "1.0", "sets": []},
                "builds": {"version": "1.0", "builds": []}
            }
        
        # Parse inventory data from files
        files = inventory_gist["files"]
        return {
            "profile": json.loads(files.get("profile.json", {"content": '{"version":"1.0","name":null,"class":null}'})["content"]),
            "gems": json.loads(files.get("gems.json", {"content": '{"version":"1.0","gems":[]}'})["content"]),
            "sets": json.loads(files.get("sets.json", {"content": '{"version":"1.0","sets":[]}'})["content"]),
            "builds": json.loads(files.get("builds.json", {"content": '{"version":"1.0","builds":[]}'})["content"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
