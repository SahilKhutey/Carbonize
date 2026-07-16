"""
Password hashing and validation.
"""

import re
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from cbms_api.config import get_settings
from cbms_shared.exceptions import ValidationFailedError


settings = get_settings()
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_cost_factor,
)


# Common passwords to reject (top 1000 list can be added)
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123",
    "password1", "admin", "letmein", "welcome", "monkey",
}


class PasswordService:
    """Service for password hashing and validation."""
    
    def validate_password_strength(self, password: str) -> None:
        """
        Validate password meets strength requirements.
        """
        if len(password) < settings.password_min_length:
            raise ValidationFailedError(
                f"Password must be at least {settings.password_min_length} characters",
                field="password",
            )
        
        if password.lower() in COMMON_PASSWORDS:
            raise ValidationFailedError(
                "Password is too common; please choose a different one",
                field="password",
            )
        
        # Complexity checks
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValidationFailedError(
                "Password must contain uppercase, lowercase, digit, and special character",
                field="password",
            )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain, hashed)
        except UnknownHashError:
            return False


password_service = PasswordService()
