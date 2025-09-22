"""
User schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
import re
from .base import BaseSchema
from .role import Role
from .tool import Tool

class UserBase(BaseModel):
    """Base user schema"""
    full_name: str
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for creating users"""
    password: str
    role_ids: List[int] = []
    tool_ids: List[int] = []
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Full name cannot be empty')
        return v.strip()

class UserUpdate(BaseModel):
    """Schema for updating users"""
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_ids: Optional[List[int]] = None
    tool_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 50:
                raise ValueError('Username must be between 3 and 50 characters')
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers, and underscores')
            return v.lower()
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError('Full name cannot be empty')
        return v.strip() if v is not None else v

class User(BaseSchema, UserBase):
    """User response schema"""
    roles: List[Role] = []
    tools: List[Tool] = []

class UserInDB(User):
    """User schema with hashed password"""
    password_hash: str