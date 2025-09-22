"""
Base model with common fields
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.db.base import Base

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)