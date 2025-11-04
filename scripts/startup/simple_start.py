"""
Simplest possible server startup - minimal dependencies
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def main():
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    print("="*60)
    print("Starting Resume Parser (Minimal Mode)")
    print("="*60)
    
    # Check minimal dependencies
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("[OK] Core packages found")
    except ImportError as e:
        print(f"[ERROR] Missing package: {e}")
        print("\nInstall minimal dependencies:")
        print("  python -m pip install -r requirements-minimal.txt")
        print("\nOr install individually:")
        print("  python -m pip install fastapi uvicorn sqlalchemy pydantic")
        sys.exit(1)
    
    # Test app import
    try:
        from app.main import app
        print("[OK] App module loaded")
    except Exception as e:
        print(f"[ERROR] Failed to import app: {e}")
        print("\nMake sure you're in the project root directory")
        sys.exit(1)
    
    # Set SQLite database
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("DATABASE_URL=sqlite:///./resume_parser.db\n")
            f.write("ENVIRONMENT=development\n")
        print("[OK] Created .env file with SQLite")
    
    print("\nServer starting on http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press CTRL+C to stop\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to avoid multiprocessing issues
            log_level="info"
        )
    except Exception as e:
        print(f"\n[ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()
        print("\nTry:")
        print("  1. python -m pip install fastapi uvicorn sqlalchemy pydantic")
        print("  2. Check if port 8000 is in use")
        sys.exit(1)

if __name__ == "__main__":
    main()

