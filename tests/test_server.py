"""
Quick test to verify server can start
"""
import sys

print("Testing server startup...")
print("=" * 50)

# Test 1: Check imports
print("\n1. Testing imports...")
try:
    from fastapi import FastAPI
    from app.main import app
    print("   ✓ FastAPI and app imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("   Solution: Run 'pip install -r requirements.txt'")
    sys.exit(1)

# Test 2: Check database connection (non-blocking)
print("\n2. Testing database connection...")
try:
    from app.db.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("   [OK] Database connection OK")
except Exception as e:
    print(f"   [WARNING] Database connection failed: {e}")
    print("   Solution: Start PostgreSQL with 'docker-compose up -d db'")
    print("   Or server will start but database operations may fail")

# Test 3: Check routes
print("\n3. Testing routes...")
try:
    routes = [route.path for route in app.routes]
    print(f"   [OK] Found {len(routes)} routes")
    print(f"   Routes: {', '.join(routes[:5])}...")
except Exception as e:
    print(f"   [ERROR] Error checking routes: {e}")

print("\n" + "=" * 50)
print("[OK] Server test complete!")
print("\nTo start the server, run:")
print("  python run_local.py")
print("  OR")
print("  uvicorn app.main:app --reload")
print("\nThen open: http://localhost:8000/docs")

