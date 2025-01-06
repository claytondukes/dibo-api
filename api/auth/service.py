"""Authentication service."""

import json
import secrets
from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status, Depends

from api.core.config import Settings, get_settings


class AuthService:
    """Service for handling GitHub authentication."""
    
    # Class-level state storage
    _states = {}

    def __init__(self, settings: Settings):
        """Initialize the auth service."""
        self.settings = settings

    def generate_github_login_url(self) -> Dict[str, str]:
        """Generate GitHub OAuth login URL with state."""
        state = secrets.token_urlsafe(32)
        self.__class__._states[state] = True  # Store state

        auth_url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self.settings.DEV_GITHUB_CLIENT_ID}"
            f"&redirect_uri={str(self.settings.DEV_GITHUB_CALLBACK_URL)}"
            "&scope=read:user user:email gist read:gist write:gist"
            f"&state={state}"
        )

        return {
            "auth_url": auth_url,
            "state": state
        }

    def validate_state(self, state: str) -> bool:
        """Validate the state parameter."""
        is_valid = self.__class__._states.get(state, False)
        if is_valid:
            del self.__class__._states[state]  # Remove used state
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
            try:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    json={
                        "client_id": self.settings.DEV_GITHUB_CLIENT_ID,
                        "client_secret": self.settings.DEV_GITHUB_CLIENT_SECRET,
                        "code": code,
                        "redirect_uri": str(self.settings.DEV_GITHUB_CALLBACK_URL)
                    }
                )

                # Parse response first to handle GitHub error responses
                data = response.json()
                
                if "error" in data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=data.get("error_description", "Token exchange failed")
                    )

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid GitHub credentials"
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange code for token"
                    )

                return data
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to connect to GitHub: {str(e)}"
                )

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

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            elif response.status_code != 200:
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

    async def get_generated_build(self, access_token: str, gist_id: str) -> Dict:
        """Get a generated build from a gist."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/gists/{gist_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid GitHub token"
                )
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Build not found"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch build"
                )
            
            gist_data = response.json()
            if not gist_data["files"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Build file not found in gist"
                )
            
            # Get the first file's content
            first_file = next(iter(gist_data["files"].values()))
            try:
                import json
                build_data = json.loads(first_file["content"])
                return {"build": build_data}
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid build data format"
                )

    async def save_generated_build(self, access_token: str, gist_id: str, build_data: Dict) -> Dict:
        """Save a generated build to a gist."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "files": {
                        "build.json": {
                            "content": json.dumps(build_data, indent=2)
                        }
                    }
                }
            )
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid GitHub token"
                )
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Build not found"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update build"
                )
            
            gist_data = response.json()
            if not gist_data["files"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Build file not found in gist"
                )
            
            # Get the first file's content
            first_file = next(iter(gist_data["files"].values()))
            try:
                updated_build = json.loads(first_file["content"])
                return {"build": updated_build}
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid build data format"
                )


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    """Get AuthService instance."""
    return AuthService(settings)
