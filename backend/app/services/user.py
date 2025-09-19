"""
User service
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.tool import Tool
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """User management service"""
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username.lower()).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email.lower()).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        # Check if username exists
        if UserService.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        if UserService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            full_name=user_data.full_name,
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password_hash=hashed_password,
            is_active=user_data.is_active
        )
        
        # Add roles
        if user_data.role_ids:
            roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            db_user.roles = roles
        
        # Add tools (only if not superuser)
        has_superuser = any(role.name == "superuser" for role in db_user.roles)
        if not has_superuser and user_data.tool_ids:
            tools = db.query(Tool).filter(Tool.id.in_(user_data.tool_ids)).all()
            db_user.tools = tools
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        # Update basic fields
        update_data = user_data.dict(exclude_unset=True, exclude={"role_ids", "tool_ids"})
        
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        if "username" in update_data:
            update_data["username"] = update_data["username"].lower()
            # Check username uniqueness
            existing = UserService.get_user_by_username(db, update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()
            # Check email uniqueness
            existing = UserService.get_user_by_email(db, update_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        # Update roles
        if user_data.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            db_user.roles = roles
        
        # Update tools (only if not superuser)
        if user_data.tool_ids is not None:
            has_superuser = any(role.name == "superuser" for role in db_user.roles)
            if not has_superuser:
                tools = db.query(Tool).filter(Tool.id.in_(user_data.tool_ids)).all()
                db_user.tools = tools
            else:
                db_user.tools = []  # Superusers get all tools automatically
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def has_role(user: User, role_name: str) -> bool:
        """Check if user has specific role"""
        return any(role.name == role_name for role in user.roles)
    
    @staticmethod
    def has_tool_access(user: User, tool_name: str, db: Session) -> bool:
        """Check if user has access to specific tool"""
        # Superusers have access to all tools
        if UserService.has_role(user, "superuser"):
            return True
        
        # Check if user has the specific tool assigned
        return any(tool.name == tool_name for tool in user.tools)
    
    @staticmethod
    def get_user_tools(user: User, db: Session) -> List[Tool]:
        """Get all tools accessible to user"""
        if UserService.has_role(user, "superuser"):
            # Superusers get all active tools
            return db.query(Tool).filter(Tool.is_active == True).all()
        else:
            # Regular users get assigned tools
            return [tool for tool in user.tools if tool.is_active]