#!/usr/bin/env python3
"""
Database migration runner script for Crash Lens application.

This script helps run Alembic migrations with proper error handling.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


def check_database_connection():
    """Check if the database is accessible."""
    try:
        # Use the same URL from alembic.ini
        database_url = "postgresql+asyncpg://postgres:postgres@tidb-hackathon-instance.cdgkfoacvf6u.us-east-1.rds.amazonaws.com:5432/postgres"
        # Convert to sync URL for connection check
        sync_url = database_url.replace("+asyncpg", "")
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure the database is running and accessible.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def run_migrations():
    """Run Alembic migrations."""
    try:
        # Get the alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Check current migration status
        print("📊 Checking current migration status...")
        command.current(alembic_cfg)
        
        # Run migrations
        print("🚀 Running migrations...")
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def show_migration_history():
    """Show migration history."""
    try:
        alembic_cfg = Config("alembic.ini")
        print("📚 Migration History:")
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Failed to show history: {e}")


def main():
    """Main function."""
    print("🔧 Crash Lens Database Migration Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command_arg = sys.argv[1].lower()
        
        if command_arg == "check":
            check_database_connection()
        elif command_arg == "history":
            show_migration_history()
        elif command_arg == "migrate":
            if check_database_connection():
                run_migrations()
        else:
            print("Usage: python run_migrations.py [check|history|migrate]")
            print("  check   - Check database connection")
            print("  history - Show migration history")
            print("  migrate - Run migrations")
    else:
        # Default behavior: check connection and run migrations
        if check_database_connection():
            run_migrations()
        else:
            print("\n💡 Try running: python run_migrations.py check")
            print("   to diagnose connection issues.")


if __name__ == "__main__":
    main()
