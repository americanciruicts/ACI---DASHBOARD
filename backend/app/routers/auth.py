"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token, RefreshRequest, RefreshResponse, ResetPasswordWithCurrentRequest, PasswordResetResponse
from app.schemas.user import User as UserSchema
from app.services.auth import AuthService
from app.services.user import UserService
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint that returns access and refresh tokens
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = AuthService.create_user_tokens(user)
    
    # Get user tools (superusers get all tools, others get assigned tools)
    user_tools = UserService.get_user_tools(user, db)
    
    # Prepare user schema with tools
    user_schema = UserSchema.model_validate(user)
    user_schema.tools = [tool for tool in user_tools]
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=user_schema
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    username = AuthService.verify_refresh_token(refresh_data.refresh_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = UserService.get_user_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, access_token_expires)
    
    return RefreshResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard tokens)
    """
    return {"message": "Successfully logged out"}

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: ResetPasswordWithCurrentRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with current password verification
    """
    # Authenticate user with current password
    login_data = LoginRequest(username=request.username, password=request.current_password)
    user = AuthService.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or current password"
        )
    
    # Validate new password strength
    if not AuthService.validate_password_strength(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        )
    
    # Reset password
    success = AuthService.reset_password_by_username(db, request.username, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )
    
    return PasswordResetResponse(message="Password successfully reset")

# /me endpoint is available at /api/v1/users/me