"""
Role schemas
"""

from typing import Optional
from pydantic import BaseModel
from .base import BaseSchema

class RoleBase(BaseModel):
    """Base role schema"""
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """Schema for creating roles"""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating roles"""
    name: Optional[str] = None
    description: Optional[str] = None

class Role(BaseSchema, RoleBase):
    """Role response schema"""
    pass