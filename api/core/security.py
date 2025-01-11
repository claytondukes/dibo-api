"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from .config import get_settings


settings = get_settings()


class Token(BaseModel):
    """Token model."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    
    sub: str  # GitHub username
    exp: datetime
    scope: str = "api"


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT access token.
    
    Args:
        subject: Token subject (typically username)
        expires_delta: Optional token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = TokenData(
        sub=subject,
        exp=expire,
    )
    
    encoded_jwt = jwt.encode(
        to_encode.model_dump(),
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        token_data = TokenData(**payload)
        
        if datetime.now(timezone.utc) > token_data.exp:
            raise JWTError("Token has expired")
        
        return token_data
        
    except JWTError as e:
        raise JWTError(f"Could not validate credentials: {str(e)}")
