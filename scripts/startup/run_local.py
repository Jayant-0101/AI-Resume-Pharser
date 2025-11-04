"""
Local development server runner with better error handling
"""
import sys
import os
import subprocess
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2',
        'pydantic', 'pydantic_settings'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("[OK] All required packages installed")
    return True

def check_database():
    """Check database connection"""
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        
        print(f"Checking database connection: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")
        
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Start PostgreSQL: docker-compose up -d db")
        print("2. Check DATABASE_URL in .env file")
        print("3. Wait 30 seconds for database to be ready")
        return False

def check_spacy_model():
    """Check if spaCy model is installed"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("[OK] spaCy model loaded")
        return True
    except OSError:
        print("[WARNING] spaCy model not found. Downloading...")
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            print("[OK] spaCy model downloaded")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to download spaCy model: {str(e)}")
            print("Run manually: python -m spacy download en_core_web_sm")
            return False

def run_server():
    """Run the development server"""
    import uvicorn
    from app.core.config import settings
    
    print(f"\n[STARTING] Server on http://localhost:{settings.API_PORT}")
    print(f"[INFO] API docs: http://localhost:{settings.API_PORT}/docs")
    print("\nPress CTRL+C to stop\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Server stopped")
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if port 8000 is already in use")
        print("2. Verify all dependencies are installed")
        print("3. Check database connection")
        sys.exit(1)

def main():
    """Main entry point"""
    print("=" * 60)
    print("Intelligent Resume Parser - Local Development Server")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check spaCy model
    check_spacy_model()
    
    # Check database (non-blocking)
    db_ok = check_database()
    if not db_ok:
        print("\n[WARNING] Database check failed. Server will start but may have issues.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()

