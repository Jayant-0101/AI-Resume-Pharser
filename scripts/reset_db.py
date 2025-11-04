"""
Quick Database Reset Script
Resets the entire database (deletes all data and resets IDs)
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.database import engine, SessionLocal, Base
from app.db.models import Resume, ParsedResumeData
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """Reset the entire database"""
    print("=" * 70)
    print("Database Reset Tool")
    print("=" * 70)
    print()
    
    print("[WARNING] This will delete ALL data from the database!")
    print("   All resumes, parsed data, and related records will be deleted.")
    print()
    
    response = input("Type 'RESET' to confirm: ")
    if response != 'RESET':
        print("Operation cancelled.")
        return
    
    print()
    print("Resetting database...")
    
    db = SessionLocal()
    try:
        # Delete all records
        deleted_parsed = db.query(ParsedResumeData).delete()
        deleted_resumes = db.query(Resume).delete()
        db.commit()
        
        print(f"   Deleted {deleted_resumes} resume records")
        print(f"   Deleted {deleted_parsed} parsed data records")
        
        # Reset sequences based on database type
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite: Reset sequence table
            db.execute(text("DELETE FROM sqlite_sequence WHERE name='resumes'"))
            db.execute(text("DELETE FROM sqlite_sequence WHERE name='parsed_resume_data'"))
            db.commit()
            print("   Reset SQLite sequences")
            
        elif settings.DATABASE_URL.startswith("postgresql"):
            # PostgreSQL: Reset sequences
            db.execute(text("ALTER SEQUENCE resumes_id_seq RESTART WITH 1"))
            db.execute(text("ALTER SEQUENCE parsed_resume_data_id_seq RESTART WITH 1"))
            db.commit()
            print("   Reset PostgreSQL sequences")
        
        print()
        print("=" * 70)
        print("[SUCCESS] Database reset successfully!")
        print("=" * 70)
        print()
        print("Next resume ID will start from 1")
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 70)
        print(f"[ERROR] Error: {e}")
        print("=" * 70)
        logger.error(f"Database reset error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()

