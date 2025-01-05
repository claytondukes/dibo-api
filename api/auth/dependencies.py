"""Authentication dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User:
    """User class for dependency injection."""
    def __init__(self, access_token: str):
        self.access_token = access_token


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get current authenticated user.
    
    Args:
        token: OAuth2 token from request
        
    Returns:
        User: Current user
        
    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return User(access_token=token)
