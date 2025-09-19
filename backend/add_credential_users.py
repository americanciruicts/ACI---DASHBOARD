"""
Add users from USER_CREDENTIALS.md to the database
Replaces existing users with the correct usernames and passwords
"""

import os
import sys
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.tool import Tool
from app.core.security import get_password_hash

def add_credential_users(db: Session):
    """Add users from USER_CREDENTIALS.md file"""

    # Users from USER_CREDENTIALS.md
    credential_users = [
        # Super Users
        {
            "full_name": "Administrator",
            "username": "admin",
            "email": "admin@americancircuits.com",
            "password": "admin",
            "roles": ["superuser"],
            "tools": []  # SuperUsers get all tools automatically
        },
        {
            "full_name": "Tony",
            "username": "tony",
            "email": "tony@americancircuits.com",
            "password": "AhFnrAASWN0a",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Preet",
            "username": "preet",
            "email": "preet@americancircuits.com",
            "password": "AaWtgE1hRECG",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Kanav",
            "username": "kanav",
            "email": "kanav@americancircuits.com",
            "password": "XCSkRBUbQKdY",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Khash",
            "username": "khash",
            "email": "khash@americancircuits.com",
            "password": "9OHRzT69Y3AZ",
            "roles": ["superuser"],
            "tools": []
        },

        # Manager/Users
        {
            "full_name": "Max",
            "username": "max",
            "email": "max@americancircuits.com",
            "password": "CCiYxAAxyR0z",
            "roles": ["user", "manager"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Ket",
            "username": "ket",
            "email": "ket@americancircuits.com",
            "password": "jzsNCHDdFGJv",
            "roles": ["user", "manager"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Julia",
            "username": "julia",
            "email": "julia@americancircuits.com",
            "password": "SkqtODKmrLjW",
            "roles": ["user", "manager"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Praful",
            "username": "praful",
            "email": "praful@americancircuits.com",
            "password": "F1Cur8klq4pe",
            "roles": ["user", "manager"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Kris",
            "username": "kris",
            "email": "kris@americancircuits.com",
            "password": "RSoX1Qcmc3Tu",
            "roles": ["user", "manager", "operator"],
            "tools": ["compare_tool"]
        },

        # Regular Users
        {
            "full_name": "Bob",
            "username": "bob",
            "email": "bob@americancircuits.com",
            "password": "n6mTWAOhVDda",
            "roles": ["user"],
            "tools": ["compare_tool"]
        },

        # User/Operators
        {
            "full_name": "Adam",
            "username": "adam",
            "email": "adam@americancircuits.com",
            "password": "5AdsYCEqrrIg",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Alex",
            "username": "alex",
            "email": "alex@americancircuits.com",
            "password": "zQE3SqCV5zAE",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Pratiksha",
            "username": "pratiksha",
            "email": "pratiksha@americancircuits.com",
            "password": "hUDcvxtL26I9",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Abhishek",
            "username": "abhishek",
            "email": "abhi@americancircuits.com",
            "password": "2umk93LcQ5cX",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]
        },

        # User/Operator/ITAR
        {
            "full_name": "Cathy",
            "username": "cathy",
            "email": "cathy@americancircuits.com",
            "password": "KOLCsB4kTzow",
            "roles": ["user", "operator", "itra"],
            "tools": ["compare_tool"]
        },
        {
            "full_name": "Larry",
            "username": "larry",
            "email": "larry@americancircuits.com",
            "password": "AaWtgE1hRECG",
            "roles": ["user", "manager", "operator", "itra"],
            "tools": ["compare_tool"]
        }
    ]

    print("🔄 Clearing existing users and relationships...")
    # Clear relationships first, then users
    from sqlalchemy import text
    db.execute(text("DELETE FROM user_tools"))
    db.execute(text("DELETE FROM user_roles"))
    db.execute(text("DELETE FROM users"))
    db.commit()

    print("👥 Creating users from USER_CREDENTIALS.md...")

    # Get available roles and tools
    all_roles = {role.name: role for role in db.query(Role).all()}
    all_tools = {tool.name: tool for tool in db.query(Tool).all()}

    for user_data in credential_users:
        try:
            # Create user
            user = User(
                full_name=user_data["full_name"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                is_active=True
            )

            # Add roles
            for role_name in user_data["roles"]:
                if role_name in all_roles:
                    user.roles.append(all_roles[role_name])

            # Add tools (or all tools for superusers)
            if "superuser" in user_data["roles"]:
                # Superusers get all tools
                user.tools = list(all_tools.values())
            else:
                # Regular users get specified tools
                for tool_name in user_data["tools"]:
                    if tool_name in all_tools:
                        user.tools.append(all_tools[tool_name])

            db.add(user)
            print(f"  ✓ Created user: {user_data['full_name']} ({user_data['username']})")

        except Exception as e:
            print(f"  ❌ Error creating user {user_data['username']}: {e}")

    db.commit()
    print("✅ All users from USER_CREDENTIALS.md have been created!")

def main():
    """Main function"""
    print("🌱 Adding users from USER_CREDENTIALS.md...")
    print("=" * 60)

    # Create database session
    db = SessionLocal()

    try:
        add_credential_users(db)

        # Display summary
        total_users = db.query(User).count()
        print("=" * 60)
        print("📊 USER CREATION SUMMARY")
        print("=" * 60)
        print(f"Total users created: {total_users}")

        # List all users
        users = db.query(User).all()
        print("\n👥 USER LIST:")
        for user in users:
            roles = [role.name for role in user.roles]
            print(f"  • {user.full_name} ({user.username}) - Roles: {', '.join(roles)}")

        print("\n✅ Database updated successfully!")
        print("🔐 You can now login with any of the credentials from USER_CREDENTIALS.md")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()