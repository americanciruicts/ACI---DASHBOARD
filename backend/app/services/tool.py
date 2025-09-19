"""
Tool service
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate

class ToolService:
    """Tool management service"""
    
    @staticmethod
    def get_tool(db: Session, tool_id: int) -> Optional[Tool]:
        """Get tool by ID"""
        return db.query(Tool).filter(Tool.id == tool_id).first()
    
    @staticmethod
    def get_tool_by_name(db: Session, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return db.query(Tool).filter(Tool.name == name).first()
    
    @staticmethod
    def get_tools(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Tool]:
        """Get all tools with pagination"""
        query = db.query(Tool)
        if active_only:
            query = query.filter(Tool.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_tool(db: Session, tool_data: ToolCreate) -> Tool:
        """Create new tool"""
        db_tool = Tool(**tool_data.dict())
        db.add(db_tool)
        db.commit()
        db.refresh(db_tool)
        return db_tool
    
    @staticmethod
    def update_tool(db: Session, tool_id: int, tool_data: ToolUpdate) -> Optional[Tool]:
        """Update tool"""
        db_tool = ToolService.get_tool(db, tool_id)
        if not db_tool:
            return None
        
        update_data = tool_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tool, field, value)
        
        db.commit()
        db.refresh(db_tool)
        return db_tool
    
    @staticmethod
    def delete_tool(db: Session, tool_id: int) -> bool:
        """Delete tool"""
        db_tool = ToolService.get_tool(db, tool_id)
        if not db_tool:
            return False
        
        db.delete(db_tool)
        db.commit()
        return True