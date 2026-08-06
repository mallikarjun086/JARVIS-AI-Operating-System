"""
Pydantic Schemas for User Accounts and Auth Tokens.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base shared user attributes."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Payload schema to register a new user."""
    password: str


class UserUpdate(BaseModel):
    """Payload schema to update user profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class Token(BaseModel):
    """OAuth2 JWT token response payload."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token claim data."""
    user_id: Optional[str] = None
