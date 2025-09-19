"""
Tool model
"""

from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class Tool(BaseModel):
    """Tool model for user access control"""
    __tablename__ = "tools"
    
    name = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String)
    route = Column(String, nullable=False)
    icon = Column(String, default="tool")
    is_active = Column(Boolean, default=True)