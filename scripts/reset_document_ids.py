"""
Reset Document IDs Script
Resets all resume document IDs to start from 0/1
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.db.models import Resume, ParsedResumeData
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_sqlite_ids():
    """Reset IDs for SQLite database"""
    logger.info("Resetting SQLite database IDs...")
    
    db = SessionLocal()
    try:
        # Delete all records
        db.query(ParsedResumeData).delete()
        db.query(Resume).delete()
        db.commit()
        
        # Reset SQLite sequence
        db.execute(text("DELETE FROM sqlite_sequence WHERE name='resumes'"))
        db.execute(text("DELETE FROM sqlite_sequence WHERE name='parsed_resume_data'"))
        db.commit()
        
        logger.info("[SUCCESS] SQLite IDs reset successfully")
        logger.info("Next resume ID will start from 1")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting SQLite IDs: {e}")
        raise
    finally:
        db.close()


def reset_postgresql_ids():
    """Reset IDs for PostgreSQL database"""
    logger.info("Resetting PostgreSQL database IDs...")
    
    db = SessionLocal()
    try:
        # Delete all records
        db.query(ParsedResumeData).delete()
        db.query(Resume).delete()
        db.commit()
        
        # Reset PostgreSQL sequences
        db.execute(text("ALTER SEQUENCE resumes_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE parsed_resume_data_id_seq RESTART WITH 1"))
        db.commit()
        
        logger.info("[SUCCESS] PostgreSQL IDs reset successfully")
        logger.info("Next resume ID will start from 1")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting PostgreSQL IDs: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function"""
    print("=" * 70)
    print("Reset Document IDs")
    print("=" * 70)
    print()
    
    # Confirm action
    print("[WARNING] This will delete ALL resume records!")
    print("   All parsed resumes and their data will be permanently deleted.")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    print()
    print("Resetting document IDs...")
    print()
    
    try:
        # Check database type and reset accordingly
        if settings.DATABASE_URL.startswith("sqlite"):
            reset_sqlite_ids()
        elif settings.DATABASE_URL.startswith("postgresql"):
            reset_postgresql_ids()
        else:
            logger.error(f"Unsupported database type: {settings.DATABASE_URL}")
            print("[ERROR] Unsupported database. Only SQLite and PostgreSQL are supported.")
            return
        
        print()
        print("=" * 70)
        print("[SUCCESS] Document IDs reset successfully!")
        print("=" * 70)
        print()
        print("Next uploaded resume will have ID: 1")
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"[ERROR] Error: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

