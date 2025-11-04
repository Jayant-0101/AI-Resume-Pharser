"""
Simple server startup script with auto-install
"""
import sys
import subprocess
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def install_requirements():
    """Install requirements if not already installed"""
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("[OK] Dependencies are installed")
        return True
    except ImportError:
        print("[INFO] Dependencies not found.")
        print("\nTo install dependencies, run one of:")
        print("  1. pip install -r requirements-dev.txt  (recommended - uses SQLite)")
        print("  2. install_windows.bat  (Windows batch script)")
        print("  3. pip install -r requirements.txt  (includes PostgreSQL)")
        print("\nFor now, trying minimal install...")
        
        try:
            # Install minimal set
            packages = [
                "fastapi==0.109.0",
                "uvicorn[standard]==0.27.0", 
                "python-multipart==0.0.6",
                "sqlalchemy==2.0.25",
                "pydantic==2.5.3",
                "pydantic-settings==2.1.0",
                "python-dotenv==1.0.1"
            ]
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
            print("[OK] Core packages installed")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install: {e}")
            print("\nPlease install manually:")
            print("  pip install -r requirements-dev.txt")
            return False

def check_spacy():
    """Check and install spaCy model (optional)"""
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("[OK] spaCy model is ready")
        return True
    except (OSError, ImportError):
        print("[INFO] spaCy model not found (optional)")
        print("Server will still work, but NLP features may be limited")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n" + "="*60)
    print("Starting Intelligent Resume Parser API")
    print("="*60)
    print("\nServer will be available at:")
    print("  - Main: http://localhost:8000")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Health: http://localhost:8000/health")
    print("\nNote: Using SQLite database (no PostgreSQL needed)")
    print("Press CTRL+C to stop the server\n")
    
    try:
        import uvicorn
        from app.core.config import settings
        
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"[ERROR] Missing package: {e}")
        print("Install dependencies: pip install -r requirements-dev.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure port 8000 is not in use")
        print("2. Check if all dependencies are installed")
        print("3. Try: pip install -r requirements-dev.txt")
        sys.exit(1)

def main():
    """Main entry point"""
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("requirements.txt"):
        print("[ERROR] Please run this script from the project root directory")
        sys.exit(1)
    
    # Set SQLite as default for easy local development
    if not os.path.exists(".env"):
        print("[INFO] Creating .env file with SQLite database...")
        with open(".env", "w") as f:
            f.write("DATABASE_URL=sqlite:///./resume_parser.db\n")
            f.write("ENVIRONMENT=development\n")
    
    # Install requirements
    if not install_requirements():
        print("\n[ERROR] Please install dependencies first:")
        print("  pip install -r requirements-dev.txt")
        sys.exit(1)
    
    # Check spaCy (non-blocking)
    check_spacy()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
