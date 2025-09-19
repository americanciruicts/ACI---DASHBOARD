"""
Tool schemas
"""

from typing import Optional
from pydantic import BaseModel
from .base import BaseSchema

class ToolBase(BaseModel):
    """Base tool schema"""
    name: str
    display_name: str
    description: Optional[str] = None
    route: str
    icon: str = "tool"
    is_active: bool = True

class ToolCreate(ToolBase):
    """Schema for creating tools"""
    pass

class ToolUpdate(BaseModel):
    """Schema for updating tools"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    route: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class Tool(BaseSchema, ToolBase):
    """Tool response schema"""
    pass