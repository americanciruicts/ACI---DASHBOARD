"""
Role model
"""

from sqlalchemy import Column, String
from .base import BaseModel

class Role(BaseModel):
    """Role model for user permissions"""
    __tablename__ = "roles"
    
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)