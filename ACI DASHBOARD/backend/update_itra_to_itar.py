#!/usr/bin/env python3
"""
Script to update ITRA role to ITAR role in the database
"""

import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.database import SessionLocal

def update_itra_to_itar():
    """Update ITRA role to ITAR in the database"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting ITRA to ITAR role update...")
        
        # Check if ITRA role exists
        result = db.execute(text("SELECT id, name, description FROM roles WHERE name = 'itra'"))
        itra_role = result.first()
        
        if itra_role:
            print(f"✅ Found ITRA role: {itra_role.name} - {itra_role.description}")
            
            # Update the role name and description
            db.execute(text("UPDATE roles SET name = 'itar', description = 'ITAR role' WHERE name = 'itra'"))
            db.commit()
            
            print("✅ Successfully updated ITRA role to ITAR role")
            
            # Verify the update
            result = db.execute(text("SELECT id, name, description FROM roles WHERE name = 'itar'"))
            itar_role = result.first()
            
            if itar_role:
                print(f"✅ Verification: Role updated to {itar_role.name} - {itar_role.description}")
            
        else:
            print("❌ ITRA role not found in database")
            
            # Check if ITAR role already exists
            result = db.execute(text("SELECT id, name, description FROM roles WHERE name = 'itar'"))
            itar_role = result.first()
            
            if itar_role:
                print(f"✅ ITAR role already exists: {itar_role.name} - {itar_role.description}")
            else:
                print("❌ Neither ITRA nor ITAR role found")
        
        # Show all current roles
        print("\n📋 Current roles in database:")
        result = db.execute(text("SELECT name, description FROM roles ORDER BY name"))
        roles = result.fetchall()
        
        for role in roles:
            print(f"  • {role.name}: {role.description}")
            
        # Show users with ITAR role
        print("\n👥 Users with ITAR role:")
        result = db.execute(text("""
            SELECT u.username, u.full_name, u.email 
            FROM users u 
            JOIN user_roles ur ON u.id = ur.user_id 
            JOIN roles r ON ur.role_id = r.id 
            WHERE r.name = 'itar'
            ORDER BY u.username
        """))
        itar_users = result.fetchall()
        
        if itar_users:
            for user in itar_users:
                print(f"  • {user.username} ({user.full_name}) - {user.email}")
        else:
            print("  No users found with ITAR role")
            
    except Exception as e:
        print(f"❌ Error updating role: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_itra_to_itar()