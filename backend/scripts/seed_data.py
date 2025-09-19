"""
Seed data script for ACI Dashboard
This script creates initial roles, tools, and users in the database
"""

import os
import sys
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, engine
from database.models import Base, User, Role, Tool

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_roles(db: Session):
    """Create initial roles"""
    roles_data = [
        {"name": "super_user", "description": "Super User with full access"},
        {"name": "manager", "description": "Manager with full access to all tools"},
        {"name": "user", "description": "Regular user"},
        {"name": "operator", "description": "Operator role"}
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"Created role: {role_data['name']}")
    
    db.commit()

def create_tools(db: Session):
    """Create initial tools"""
    tools_data = [
        {
            "name": "compare_tool",
            "display_name": "BOM Compare Tool",
            "description": "BOM comparison and analysis tool",
            "route": "/dashboard/tools/compare",
            "icon": "compare"
        },
    ]
    
    for tool_data in tools_data:
        existing_tool = db.query(Tool).filter(Tool.name == tool_data["name"]).first()
        if not existing_tool:
            tool = Tool(**tool_data)
            db.add(tool)
            print(f"Created tool: {tool_data['display_name']}")
    
    db.commit()

def create_users(db: Session):
    """Create initial users with hashed passwords"""
    # Complete user credentials list as specified
    sample_users = [
        # SUPERUSERS (Full Access - All Tools)
        {
            "full_name": "Tony",
            "username": "tony967",
            "email": "tony@americancircuits.com",
            "password": "AhFnrAASWN0a",
            "roles": ["super_user"],
            "tools": []  # Super user gets all tools automatically
        },
        {
            "full_name": "Preet",
            "username": "preet858",
            "email": "preet@americancircuits.com",
            "password": "AaWtgE1hRECG",
            "roles": ["super_user"],
            "tools": []
        },
        {
            "full_name": "Kanav",
            "username": "kanav651",
            "email": "kanav@americancircuits.com",
            "password": "XCSkRBUbQKdY",
            "roles": ["super_user"],
            "tools": []
        },
        {
            "full_name": "Khash",
            "username": "khash826",
            "email": "khash@americancircuits.com",
            "password": "9OHRzT69Y3AZ",
            "roles": ["super_user"],
            "tools": []
        },
        # MANAGERS (Full Access - All Tools)
        {
            "full_name": "Max",
            "username": "max463",
            "email": "max@americancircuits.com",
            "password": "CCiYxAAxyR0z",
            "roles": ["manager"],
            "tools": []  # Manager gets all tools automatically
        },
        {
            "full_name": "Ket",
            "username": "ket833",
            "email": "ket@americancircuits.com",
            "password": "jzsNCHDdFGJv",
            "roles": ["manager"],
            "tools": []
        },
        {
            "full_name": "Julia",
            "username": "julia509",
            "email": "julia@americancircuits.com",
            "password": "SkqtODKmrLjW",
            "roles": ["manager"],
            "tools": []
        },
        {
            "full_name": "Praful",
            "username": "praful396",
            "email": "praful@americancircuits.com",
            "password": "F1Cur8klq4pe",
            "roles": ["manager"],
            "tools": []
        },
        {
            "full_name": "Kris",
            "username": "kris500",
            "email": "kris@americancircuits.com",
            "password": "RSoX1Qcmc3Tu",
            "roles": ["manager"],
            "tools": []  # Multi-role manager
        },
        # USERS & OPERATORS (Compare Tool Only)
        {
            "full_name": "Adam",
            "username": "adam585",
            "email": "adam@americancircuits.com",
            "password": "5AdsYCEqrrIg",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Alex",
            "username": "alex343",
            "email": "alex@americancircuits.com",
            "password": "zQE3SqCV5zAE",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Pratiksha",
            "username": "pratiksha649",
            "email": "pratiksha@americancircuits.com",
            "password": "hUDcvxtL26I9",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Cathy",
            "username": "cathy596",
            "email": "cathy@americancircuits.com",
            "password": "KOLCsB4kTzow",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Abhishek",
            "username": "abhishek878",
            "email": "abhi@americancircuits.com",
            "password": "2umk93LcQ5cX",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Bob",
            "username": "bob771",
            "email": "bob@americancircuits.com",
            "password": "n6mTWAOhVDda",
            "roles": ["user"],
            "tools": ["compare_tool"]
        },
    ]
    
    for user_data in sample_users:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            # Hash the password
            hashed_password = get_password_hash(user_data["password"])
            
            # Create user
            user = User(
                full_name=user_data["full_name"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hashed_password,
                is_active=True
            )
            
            # Add roles to user
            for role_name in user_data["roles"]:
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    user.roles.append(role)
            
            # Add tools to user (only if not superuser or manager)
            if not any(role_name in ["super_user", "manager"] for role_name in user_data["roles"]):
                for tool_name in user_data["tools"]:
                    tool = db.query(Tool).filter(Tool.name == tool_name).first()
                    if tool:
                        user.tools.append(tool)
            
            db.add(user)
            print(f"Created user: {user_data['full_name']} ({user_data['username']})")
    
    db.commit()

def seed_database():
    """Main function to seed the database"""
    print("Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create seed data
        print("\n1. Creating roles...")
        create_roles(db)
        
        print("\n2. Creating tools...")
        create_tools(db)
        
        print("\n3. Creating users...")
        create_users(db)
        
        print("\n[SUCCESS] Database seeding completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()