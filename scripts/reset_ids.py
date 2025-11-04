"""
Reset Document IDs - Quick Script
Resets all resume IDs to start from 1
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

def reset_ids():
    """Reset document IDs"""
    print("Resetting document IDs...")
    
    db = SessionLocal()
    try:
        # Delete all records
        deleted_parsed = db.query(ParsedResumeData).delete()
        deleted_resumes = db.query(Resume).delete()
        db.commit()
        print(f"Deleted {deleted_resumes} resumes and {deleted_parsed} parsed records")
        
        # Reset sequences
        if settings.DATABASE_URL.startswith("sqlite"):
            try:
                # SQLite sequence table may not exist if no auto-increment was used
                # Try to reset it, but don't fail if it doesn't exist
                db.execute(text("DELETE FROM sqlite_sequence WHERE name='resumes'"))
                db.execute(text("DELETE FROM sqlite_sequence WHERE name='parsed_resume_data'"))
                db.commit()
                print("Reset SQLite sequences")
            except Exception as seq_error:
                # Sequence table doesn't exist or already reset, that's okay
                db.rollback()
                print("SQLite sequences already reset or not needed")
        elif settings.DATABASE_URL.startswith("postgresql"):
            db.execute(text("ALTER SEQUENCE resumes_id_seq RESTART WITH 1"))
            db.execute(text("ALTER SEQUENCE parsed_resume_data_id_seq RESTART WITH 1"))
            db.commit()
            print("Reset PostgreSQL sequences")
        
        print("[SUCCESS] Document IDs reset! Next resume will have ID: 1")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to reset IDs: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    reset_ids()

