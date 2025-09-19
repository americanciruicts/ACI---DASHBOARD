"""
Role service
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    """Role management service"""
    
    @staticmethod
    def get_role(db: Session, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """Get role by name"""
        return db.query(Role).filter(Role.name == name).first()
    
    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles with pagination"""
        return db.query(Role).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create new role"""
        db_role = Role(**role_data.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """Update role"""
        db_role = RoleService.get_role(db, role_id)
        if not db_role:
            return None
        
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Delete role"""
        db_role = RoleService.get_role(db, role_id)
        if not db_role:
            return False
        
        db.delete(db_role)
        db.commit()
        return True