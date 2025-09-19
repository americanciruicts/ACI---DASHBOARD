"""
Tool access routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import (
    get_current_active_user, 
    require_compare_tool
)
from app.models.user import User
from app.schemas.tool import Tool as ToolSchema
from app.services.user import UserService
from app.services.tool import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("/", response_model=List[ToolSchema])
async def get_user_tools(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tools assigned to current user"""
    tools = UserService.get_user_tools(current_user, db)
    return tools

@router.get("/{tool_id}", response_model=ToolSchema)
async def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific tool if user has access"""
    tool = ToolService.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Check if user has access to this tool
    user_tools = UserService.get_user_tools(current_user, db)
    if tool not in user_tools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tool"
        )
    
    return tool

# Specific tool access endpoints
@router.get("/compare/access")
async def access_compare_tool(
    current_user: User = Depends(require_compare_tool)
):
    """Access Compare Tool"""
    return {
        "message": "Compare Tool accessed successfully",
        "user": current_user.username,
        "tool": "Compare Tool"
    }


# Tool-specific functionality endpoints
@router.post("/compare/execute")
async def execute_compare_tool(
    data: dict,
    current_user: User = Depends(require_compare_tool)
):
    """Execute Compare Tool functionality"""
    return {
        "message": "Compare Tool executed",
        "user": current_user.username,
        "result": "Comparison completed",
        "data": data
    }

