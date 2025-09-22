#!/usr/bin/env python3
"""
Test script to verify database setup and migrations
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Role, Tool
from database import SessionLocal

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_tables_exist():
    """Test that all tables exist"""
    print("\n🔍 Testing table existence...")
    
    tables_to_check = ['users', 'roles', 'tools', 'user_roles', 'user_tools']
    
    try:
        db = SessionLocal()
        for table in tables_to_check:
            result = db.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
            exists = result.scalar()
            if exists:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
                return False
        
        db.close()
        print("✅ All required tables exist!")
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def test_seed_data():
    """Test that seed data was inserted"""
    print("\n🔍 Testing seed data...")
    
    try:
        db = SessionLocal()
        
        # Check roles
        roles_count = db.query(Role).count()
        print(f"📊 Found {roles_count} roles")
        
        # Check tools
        tools_count = db.query(Tool).count()
        print(f"📊 Found {tools_count} tools")
        
        # Check users
        users_count = db.query(User).count()
        print(f"📊 Found {users_count} users")
        
        # Check specific test users
        test_users = ['tony967', 'pratiksha649', 'cathy596']
        for username in test_users:
            user = db.query(User).filter(User.username == username).first()
            if user:
                print(f"✅ User '{username}' found with {len(user.roles)} roles and {len(user.tools)} tools")
            else:
                print(f"❌ User '{username}' not found")
        
        db.close()
        
        if roles_count >= 4 and tools_count >= 3 and users_count >= 3:
            print("✅ Seed data looks good!")
            return True
        else:
            print("⚠️ Seed data may be incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error checking seed data: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running database setup tests...\n")
    
    tests = [
        test_database_connection,
        test_tables_exist,
        test_seed_data
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All tests passed! Database setup is working correctly.")
    else:
        print("❌ Some tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()