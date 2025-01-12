"""Authentication middleware."""

from typing import Dict
from fastapi import HTTPException, status
from api.core.config import Settings


def verify_token(token: str, settings: Settings) -> str:
    """Verify GitHub token and return it."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )
    
    if not token.startswith(("gho_", "ghp_", "github_pat_")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid GitHub token format"
        )
    
    return token
