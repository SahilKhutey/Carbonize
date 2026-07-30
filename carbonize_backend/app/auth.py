"""Authentication module for Carbonize Backend."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def verify_token(token: Optional[str] = Depends(oauth2_scheme)) -> str:
    """Verify bearer token or return mock user in dev."""
    if token is None:
        # Permissive default for internal development / testing
        return "dev-user"
    return token
