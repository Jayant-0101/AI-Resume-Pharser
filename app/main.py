"""
Main FastAPI application entry point
"""
import logging
import traceback
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Setup basic logging immediately
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Create app FIRST before anything else ---
app = FastAPI(
    title="AI Resume Parser API",
    description="AI-powered resume parsing with Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — add immediately after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

# --- Simple health/ping routes (always available) ---
@app.get("/ping")
async def ping():
    return {
        "status": "alive",
        "db_url_set": bool(os.environ.get("DATABASE_URL")),
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "python_path": os.getcwd(),
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# --- Now load heavier dependencies (guarded) ---
_load_errors = []

# Database
try:
    from app.db.database import engine, Base
    from app.core.config import settings
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready")
    except Exception as db_err:
        logger.warning(f"DB table creation skipped: {db_err}")
except Exception as e:
    _load_errors.append(f"DB init: {e}")
    logger.error(f"DB import error: {traceback.format_exc()}")

# API routes
try:
    from app.api.v1 import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("API routes loaded")
except Exception as e:
    _load_errors.append(f"API routes: {e}")
    logger.error(f"API router error: {traceback.format_exc()}")

# Static files
try:
    from fastapi.staticfiles import StaticFiles
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info("Static files mounted")
    else:
        logger.warning(f"Static dir not found: {static_dir}")
except Exception as e:
    _load_errors.append(f"Static files: {e}")
    logger.warning(f"Static mount error: {e}")


@app.get("/")
async def root():
    """Serve UI or API info"""
    static_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return JSONResponse({
        "message": "AI Resume Parser API is running",
        "docs": "/docs",
        "health": "/health",
        "ping": "/ping",
        "load_errors": _load_errors,
    })


@app.get("/debug")
async def debug():
    """Show load errors for debugging"""
    return {
        "load_errors": _load_errors,
        "cwd": os.getcwd(),
        "db_url_set": bool(os.environ.get("DATABASE_URL")),
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
    }
