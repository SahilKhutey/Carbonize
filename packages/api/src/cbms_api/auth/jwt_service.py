"""
JWT token creation, validation, and refresh logic.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import secrets

from jose import JWTError, jwt, ExpiredSignatureError
from jose.exceptions import JWTClaimsError

from cbms_api.config import get_settings
from cbms_shared.exceptions import AuthenticationError
from cbms_shared.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


# Token types
ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"
MFA_CHALLENGE_TOKEN = "mfa_challenge"


class JWTService:
    """Service for creating and validating JWTs."""
    
    def create_access_token(
        self,
        user_id: UUID,
        org_id: UUID,
        roles: list[str],
        email: str,
        mfa_verified: bool = True,
    ) -> str:
        """
        Create a short-lived access token.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "org_id": str(org_id),
            "roles": roles,
            "email": email,
            "type": ACCESS_TOKEN,
            "mfa": mfa_verified,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    def create_refresh_token(
        self,
        user_id: UUID,
        org_id: UUID,
        token_family: str,
    ) -> str:
        """
        Create a long-lived refresh token.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "org_id": str(org_id),
            "type": REFRESH_TOKEN,
            "family": token_family,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=settings.refresh_token_ttl_days)).timestamp()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def create_mfa_challenge_token(self, user_id: UUID, org_id: UUID) -> str:
        """
        Create a short-lived MFA challenge token.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "org_id": str(org_id),
            "type": MFA_CHALLENGE_TOKEN,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    def decode_token(self, token: str, expected_type: str) -> dict:
        """
        Decode and validate a JWT.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
            )
        except ExpiredSignatureError:
            raise AuthenticationError("Token has expired", code="token_expired")
        except JWTClaimsError as e:
            raise AuthenticationError(f"Invalid token claims: {e}", code="invalid_claims")
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {e}", code="invalid_token")
        
        # Check token type
        if payload.get("type") != expected_type:
            raise AuthenticationError(
                f"Wrong token type: expected {expected_type}, got {payload.get('type')}",
                code="wrong_token_type",
            )
        
        return payload
    
    def get_user_id_from_token(self, token: str) -> UUID:
        """Extract user_id from access token."""
        payload = self.decode_token(token, ACCESS_TOKEN)
        return UUID(payload["sub"])
    
    def get_org_id_from_token(self, token: str) -> UUID:
        """Extract org_id from access token."""
        payload = self.decode_token(token, ACCESS_TOKEN)
        return UUID(payload["org_id"])


# Singleton
jwt_service = JWTService()
