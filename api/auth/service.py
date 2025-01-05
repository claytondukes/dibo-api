"""Authentication service."""

import secrets
from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status, Depends

from api.core.config import Settings, get_settings


class AuthService:
    """Service for handling GitHub authentication."""

    def __init__(self, settings: Settings):
        """Initialize the auth service."""
        self.settings = settings
        self.states = {}  # In-memory state storage

    def generate_github_login_url(self) -> Dict[str, str]:
        """Generate GitHub OAuth login URL with state."""
        state = secrets.token_urlsafe(32)
        self.states[state] = True  # Store state

        auth_url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self.settings.ACTIVE_GITHUB_CLIENT_ID}"
            f"&redirect_uri={self.settings.ACTIVE_GITHUB_CALLBACK_URL}"
            "&scope=read:user user:email gist read:gist write:gist"
            f"&state={state}"
        )

        return {
            "auth_url": auth_url,
            "state": state
        }

    def validate_state(self, state: str) -> bool:
        """Validate the state parameter."""
        is_valid = self.states.get(state, False)
        if is_valid:
            del self.states[state]  # Remove used state
        return is_valid

    async def exchange_code_for_token(
        self,
        code: str,
        state: str
    ) -> Dict[str, str]:
        """Exchange OAuth code for access token."""
        if not self.validate_state(state):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                json={
                    "client_id": self.settings.ACTIVE_GITHUB_CLIENT_ID,
                    "client_secret": self.settings.ACTIVE_GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": self.settings.ACTIVE_GITHUB_CALLBACK_URL
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data.get("error_description", "Token exchange failed")
                )

            return data

    async def get_user_gists(self, access_token: str) -> list:
        """Get user's gists from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/gists",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch gists"
                )

            return response.json()

    async def create_gist(
        self,
        access_token: str,
        filename: str,
        content: str,
        description: Optional[str] = None
    ) -> Dict:
        """Create a new GitHub gist."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.github.com/gists",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "description": description,
                    "public": False,
                    "files": {
                        filename: {
                            "content": content
                        }
                    }
                }
            )

            if response.status_code != 201:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Failed to create gist"
                )

            return response.json()

    async def update_gist(
        self,
        access_token: str,
        gist_id: str,
        filename: str,
        content: str,
        description: Optional[str] = None
    ) -> Dict:
        """Update an existing GitHub gist."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "description": description,
                    "files": {
                        filename: {
                            "content": content
                        }
                    }
                }
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Gist not found"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Failed to update gist"
                )

            return response.json()


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    """Get AuthService instance."""
    return AuthService(settings)
