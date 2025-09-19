#!/usr/bin/env python3

"""
Create a test user for the ACI Dashboard application
"""

import sys
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import User, Role, Tool

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_test_user():
    # Create tables if they don't exist
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if superuser role exists, create if not
        superuser_role = db.query(Role).filter(Role.name == "superuser").first()
        if not superuser_role:
            superuser_role = Role(name="superuser", description="Super User with full access")
            db.add(superuser_role)
            db.commit()
            print("Created superuser role")

        # Check if tools exist, create if not
        tools_data = [
            {"name": "compare_tool", "display_name": "Compare Tool", "route": "/dashboard/tools/compare", "icon": "compare", "description": "Tool for data comparison"}
        ]
        
        tools = []
        for tool_data in tools_data:
            tool = db.query(Tool).filter(Tool.name == tool_data["name"]).first()
            if not tool:
                tool = Tool(**tool_data)
                db.add(tool)
                db.commit()
                print(f"Created tool: {tool_data['display_name']}")
            tools.append(tool)

        # Check if test user exists
        test_user = db.query(User).filter(User.username == "admin").first()
        if test_user:
            print("Test user 'admin' already exists!")
            return

        # Create test user
        hashed_password = get_password_hash("admin123")
        test_user = User(
            full_name="Administrator",
            username="admin",
            email="admin@acimapping.com",
            password_hash=hashed_password,
            is_active=True
        )

        # Add roles and tools to user
        test_user.roles.append(superuser_role)
        for tool in tools:
            test_user.tools.append(tool)

        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: superuser")
        print("   Tools: All tools assigned")

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()