"""Update ITRA role to ITAR

Revision ID: 003
Revises: 002
Create Date: 2025-08-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Update the role name from 'itra' to 'itar' and description from 'ITRA role' to 'ITAR role'
    connection = op.get_bind()
    
    # Update role name and description
    connection.execute(
        text("UPDATE roles SET name = 'itar', description = 'ITAR role' WHERE name = 'itra'")
    )
    
    # Update any user references (this should be handled by foreign key, but just to be sure)
    # Note: Since we're using relationship tables, no direct updates needed for user_roles table
    
    print("✓ Successfully updated ITRA role to ITAR")

def downgrade() -> None:
    # Revert the role name back to 'itra'
    connection = op.get_bind()
    
    connection.execute(
        text("UPDATE roles SET name = 'itra', description = 'ITRA role' WHERE name = 'itar'")
    )
    
    print("✓ Successfully reverted ITAR role back to ITRA")