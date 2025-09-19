"""Seed initial data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def upgrade() -> None:
    # Create a connection to execute SQL
    connection = op.get_bind()
    
    # Insert roles
    roles_data = [
        {"name": "superuser", "description": "Super User with full access"},
        {"name": "user", "description": "Regular user"},
        {"name": "operator", "description": "Operator role"},
        {"name": "itra", "description": "ITRA role"}
    ]
    
    for role_data in roles_data:
        # Check if role already exists
        result = connection.execute(
            text("SELECT id FROM roles WHERE name = :name"),
            {"name": role_data["name"]}
        ).first()
        
        if not result:
            connection.execute(
                text("INSERT INTO roles (name, description, created_at) VALUES (:name, :description, NOW())"),
                role_data
            )
    
    # Insert tools
    tools_data = [
        {
            "name": "compare_tool",
            "display_name": "Compare Tool",
            "description": "Tool for comparing data",
            "route": "/dashboard/tools/compare",
            "icon": "compare"
        },
        {
            "name": "x_tool",
            "display_name": "X Tool",
            "description": "Advanced X functionality",
            "route": "/dashboard/tools/x-tool",
            "icon": "x-circle"
        },
        {
            "name": "y_tool",
            "display_name": "Y Tool",
            "description": "Y analysis tool",
            "route": "/dashboard/tools/y-tool",
            "icon": "y-circle"
        }
    ]
    
    for tool_data in tools_data:
        # Check if tool already exists
        result = connection.execute(
            text("SELECT id FROM tools WHERE name = :name"),
            {"name": tool_data["name"]}
        ).first()
        
        if not result:
            connection.execute(
                text("INSERT INTO tools (name, display_name, description, route, icon, is_active, created_at) VALUES (:name, :display_name, :description, :route, :icon, true, NOW())"),
                tool_data
            )
    
    # Insert sample users with hashed passwords
    sample_users = [
        {
            "full_name": "Tony",
            "username": "tony967",
            "email": "tony@americancircuits.com",
            "password": "AhFnrAASWN0a",
            "roles": ["superuser"],
            "tools": []  # Super user gets all tools automatically
        },
        {
            "full_name": "Preet",
            "username": "preet858",
            "email": "preet@americancircuits.com",
            "password": "AaWtgE1hRECG",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Kanav",
            "username": "kanav651",
            "email": "kanav@americancircuits.com",
            "password": "XCSkRBUbQKdY",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Khash",
            "username": "khash826",
            "email": "khash@americancircuits.com",
            "password": "9OHRzT69Y3AZ",
            "roles": ["superuser"],
            "tools": []
        },
        {
            "full_name": "Max",
            "username": "max463",
            "email": "max@americancircuits.com",
            "password": "CCiYxAAxyR0z",
            "roles": ["user"],
            "tools": ["compare_tool", "x_tool"]
        },
        {
            "full_name": "Pratiksha",
            "username": "pratiksha649",
            "email": "pratiksha@americancircuits.com",
            "password": "hUDcvxtL26I9",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]  # Specific assignment as requested
        },
        {
            "full_name": "Cathy",
            "username": "cathy596",
            "email": "cathy@americancircuits.com",
            "password": "KOLCsB4kTzow",
            "roles": ["user", "operator"],
            "tools": ["compare_tool"]  # Specific assignment as requested
        },
    ]
    
    for user_data in sample_users:
        # Check if user already exists
        result = connection.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": user_data["username"]}
        ).first()
        
        if not result:
            # Hash password
            hashed_password = get_password_hash(user_data["password"])
            
            # Insert user
            user_result = connection.execute(
                text("INSERT INTO users (full_name, username, email, hashed_password, is_active, created_at) VALUES (:full_name, :username, :email, :hashed_password, true, NOW()) RETURNING id"),
                {
                    "full_name": user_data["full_name"],
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "hashed_password": hashed_password
                }
            )
            user_id = user_result.scalar()
            
            # Add roles to user
            for role_name in user_data["roles"]:
                role_result = connection.execute(
                    text("SELECT id FROM roles WHERE name = :name"),
                    {"name": role_name}
                ).first()
                
                if role_result:
                    connection.execute(
                        text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                        {"user_id": user_id, "role_id": role_result.id}
                    )
            
            # Add tools to user (only if not superuser)
            if not any(role_name == "superuser" for role_name in user_data["roles"]):
                for tool_name in user_data["tools"]:
                    tool_result = connection.execute(
                        text("SELECT id FROM tools WHERE name = :name"),
                        {"name": tool_name}
                    ).first()
                    
                    if tool_result:
                        connection.execute(
                            text("INSERT INTO user_tools (user_id, tool_id) VALUES (:user_id, :tool_id)"),
                            {"user_id": user_id, "tool_id": tool_result.id}
                        )

def downgrade() -> None:
    # Remove seed data (in reverse order)
    connection = op.get_bind()
    
    # Remove user associations
    connection.execute(text("DELETE FROM user_tools"))
    connection.execute(text("DELETE FROM user_roles"))
    
    # Remove users
    connection.execute(text("DELETE FROM users"))
    
    # Remove tools
    connection.execute(text("DELETE FROM tools"))
    
    # Remove roles
    connection.execute(text("DELETE FROM roles"))