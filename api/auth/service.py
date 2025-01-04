"""Authentication service."""

import secrets
from typing import Dict, Optional, ClassVar
from urllib.parse import urlencode
import json

import httpx
from fastapi import HTTPException, status

from ..core.config import Settings, get_settings
from ..core.security import create_access_token
from .models import GitHubUser, OAuthState


class AuthService:
    """Authentication service for GitHub OAuth."""
    
    # Class-level storage for OAuth states
    _oauth_states: ClassVar[Dict[str, OAuthState]] = {}
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the auth service.
        
        Args:
            settings: Optional settings instance
        """
        self.settings = settings or get_settings()
    
    def generate_oauth_url(self) -> Dict[str, str]:
        """Generate GitHub OAuth URL and state.
        
        Returns:
            dict: OAuth URL and state
        """
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state
        AuthService._oauth_states[state] = OAuthState(
            state=state,
            redirect_uri=self.settings.active_github_callback_url
        )
        
        # Build OAuth URL
        params = {
            "client_id": self.settings.active_github_client_id,
            "redirect_uri": str(self.settings.active_github_callback_url),
            "scope": "read:user user:email gist",
            "state": state,
        }
        
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_token(
        self,
        code: str,
        state: str
    ) -> Dict[str, str]:
        """Exchange OAuth code for access token.
        
        Args:
            code: OAuth code from GitHub
            state: OAuth state for verification
            
        Returns:
            dict: Access token response
            
        Raises:
            HTTPException: If state is invalid or token exchange fails
        """
        # Verify state
        stored_state = AuthService._oauth_states.get(state)
        if not stored_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state"
            )
        
        # Clean up stored state
        del AuthService._oauth_states[state]
        
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self.settings.active_github_client_id,
                    "client_secret": self.settings.active_github_client_secret,
                    "code": code,
                    "redirect_uri": str(self.settings.active_github_callback_url),
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_response = response.json()
            github_token = token_response.get("access_token")
            if not github_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            # Get user profile
            user = await self._get_github_user(github_token)
            
            # Create JWT token
            access_token = create_access_token(subject=user.login)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "scope": token_response.get("scope", ""),
                "user": {
                    "id": str(user.id),
                    "username": user.login,
                    "avatar_url": user.avatar_url,
                    "name": user.name,
                    "email": user.email
                }
            }
    
    async def _get_github_user(self, token: str) -> GitHubUser:
        """Get GitHub user profile.
        
        Args:
            token: GitHub access token
            
        Returns:
            GitHubUser: User profile data
            
        Raises:
            HTTPException: If profile fetch fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info"
                )
            
            return GitHubUser(**response.json())

    async def get_inventory_gist(self, token: str, gist_id: Optional[str] = None) -> Dict:
        """Get user's inventory gist.
        
        Args:
            token: GitHub access token
            gist_id: Optional specific gist ID to fetch
            
        Returns:
            dict: Inventory data from gist
            
        Raises:
            HTTPException: If gist fetch fails
        """
        async with httpx.AsyncClient() as client:
            # If no specific gist_id, search for one named gems.json
            if not gist_id:
                response = await client.get(
                    "https://api.github.com/gists",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to fetch gists"
                    )
                
                gists = response.json()
                for gist in gists:
                    if "gems.json" in gist["files"]:
                        gist_id = gist["id"]
                        break
                
                if not gist_id:
                    return {}  # No inventory gist found
            
            # Fetch specific gist
            response = await client.get(
                f"https://api.github.com/gists/{gist_id}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch inventory gist"
                )
            
            gist_data = response.json()
            if "gems.json" not in gist_data["files"]:
                return {}
            
            content = gist_data["files"]["gems.json"]["content"]
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid inventory gist format"
                )


# Singleton instance
_auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return _auth_service
