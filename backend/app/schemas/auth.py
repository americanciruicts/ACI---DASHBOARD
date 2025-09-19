"""
Authentication schemas
"""

from typing import Optional
from pydantic import BaseModel
from .user import User

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str

class RefreshRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str

class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user: User

class RefreshResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str

class ResetPasswordWithCurrentRequest(BaseModel):
    """Reset password with current password verification request"""
    username: str
    current_password: str
    new_password: str

class PasswordResetResponse(BaseModel):
    """Password reset response schema"""
    message: str