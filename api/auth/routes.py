"""Authentication routes."""

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..core.config import get_settings
from .models import GitHubUser, OAuthCallback, UserProfile
from .service import AuthService


settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Singleton instance
_auth_service = AuthService(settings)


def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return _auth_service


@router.get(
    "/github/login",
    summary="Start GitHub OAuth flow",
    description="Generate OAuth URL and state for GitHub authentication"
)
async def github_login(
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Generate GitHub OAuth URL and state."""
    return auth_service.generate_oauth_url()


@router.post(
    "/github",
    summary="Complete GitHub OAuth flow",
    description="Exchange OAuth code for access token"
)
async def github_callback(
    data: OAuthCallback,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Handle GitHub OAuth callback."""
    return await auth_service.exchange_code_for_token(
        data.code,
        data.state
    )


@router.get(
    "/user",
    response_model=UserProfile,
    summary="Get user profile",
    description="Get current user's GitHub profile"
)
async def get_user_profile(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserProfile:
    """Get current user's GitHub profile."""
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Extract token
    token = token.split(" ")[1]
    
    # Get user profile
    user = await auth_service._get_github_user(token)
    
    # Convert to response format
    return UserProfile(
        id=str(user.id),
        username=user.login,
        avatar_url=str(user.avatar_url) if user.avatar_url else None,
        name=user.name,
        email=user.email
    )


@router.get(
    "/inventory",
    summary="Get user's gem inventory",
    description="Fetch the user's gem inventory from their GitHub gist"
)
async def get_inventory(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Get user's gem inventory from GitHub gist."""
    # Get token from request
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization token"
        )
    token = token.split(" ")[1]
    
    # Get inventory from gist
    return await auth_service.get_inventory_gist(token)
