#!/usr/bin/env python3
"""
Startup script for ACI Dashboard backend
This script runs database migrations and seeds the database with initial data
"""

import os
import sys
import subprocess
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aci_dashboard")
    engine = create_engine(database_url)
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return True
        except OperationalError as e:
            print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print(f"❌ Database not ready after {max_retries} attempts: {e}")
                return False
    
    return False

def run_migrations():
    """Run Alembic migrations"""
    print("\n🔄 Running database migrations...")
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            if result.stdout:
                print("Migration output:", result.stdout)
        else:
            print("❌ Migration failed!")
            print("Error:", result.stderr)
            return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed.")
        return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    return True

def seed_database():
    """Run database seeding"""
    print("\n🌱 Seeding database with initial data...")
    try:
        # Import and run seed data
        from seed_data import seed_database
        seed_database()
        return True
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting ACI Dashboard backend setup...")
    
    # Wait for database
    if not wait_for_db():
        print("❌ Could not connect to database. Exiting.")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migrations failed. Exiting.")
        sys.exit(1)
    
    # Seed database
    if not seed_database():
        print("⚠️ Database seeding failed, but continuing...")
    
    print("\n✅ Backend setup completed successfully!")
    print("🌐 Starting FastAPI server...")

if __name__ == "__main__":
    main()