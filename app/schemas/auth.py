"""Pydantic Schemas for auth endpoints"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Data required to register a new user and organization."""

    email: EmailStr                                  # Validates email format
    password: str = Field(min_length=8, max_length=128)  # Enforce password strength
    full_name: str = Field(min_length=1, max_length=255)
    org_name: str = Field(min_length=1, max_length=255)

class LoginRequest(BaseModel):
    """Data required to log in."""

    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Returned after successful login or registration."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    """Data required to refresh an access token."""
    
    refresh_token: str