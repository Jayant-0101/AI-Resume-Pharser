"""
Fast server startup - no model loading blocking
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def main():
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    print("="*60)
    print("Fast Resume Parser Server")
    print("="*60)
    print("\n[INFO] Starting server with lazy model loading...")
    print("[INFO] Models will load on demand (won't block startup)")
    print("\nServer starting on http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press CTRL+C to stop\n")
    
    try:
        import uvicorn
        
        # Start server with minimal logging to avoid model loading messages
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload
            log_level="warning",  # Reduce log noise
            access_log=False  # Disable access logs for cleaner output
        )
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Server stopped")
    except Exception as e:
        print(f"\n[ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()



