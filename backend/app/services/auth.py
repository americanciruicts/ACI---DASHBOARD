"""
Authentication service
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password, create_tokens, verify_token
from app.models.user import User
from app.schemas.auth import LoginRequest

class AuthService:
    """Authentication service"""
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Optional[User]:
        """Authenticate user by username and password"""
        user = db.query(User).filter(User.username == login_data.username.lower()).first()
        if not user:
            return None
        if not verify_password(login_data.password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def create_user_tokens(user: User) -> dict:
        """Create access and refresh tokens for user"""
        return create_tokens(user.username)
    
    @staticmethod
    def verify_refresh_token(refresh_token: str) -> Optional[str]:
        """Verify refresh token and return username"""
        return verify_token(refresh_token, "refresh")
    
    @staticmethod
    def get_user_from_token(db: Session, token: str, token_type: str = "access") -> Optional[User]:
        """Get user from JWT token"""
        username = verify_token(token, token_type)
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            return None
        
        return user