#!/usr/bin/env python3

"""
Simple test to check if our user authentication is working
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def test_login():
    db = SessionLocal()
    try:
        # Try to find the admin user
        user = db.query(User).filter(User.username == "admin").first()
        
        if not user:
            print("No user found with username 'admin'")
            return
        
        print(f"User found: {user.full_name} ({user.username})")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")
        
        # Test password
        if verify_password("admin123", user.password_hash):
            print("Password verification successful!")
        else:
            print("Password verification failed!")
            
        # Check roles
        print(f"   Roles: {[role.name for role in user.roles]}")
        print(f"   Tools: {[tool.display_name for tool in user.tools]}")
            
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_login()