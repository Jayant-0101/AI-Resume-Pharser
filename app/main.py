"""
Main FastAPI application entry point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import engine, Base

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create database tables (with error handling, non-blocking)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.warning(f"Could not create database tables: {str(e)}")
    logger.warning("This is OK if tables already exist or database is not available yet")
    # Continue anyway - tables will be created on first use

app = FastAPI(
    title="Intelligent Resume Parser API",
    description="AI-powered resume parsing system with multi-format support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Serve dashboard page
@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page"""
    try:
        return FileResponse("static/dashboard.html")
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return {"error": "Dashboard not available"}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=FileResponse)
async def root():
    """Root endpoint - serve web interface"""
    import os
    static_path = os.path.join("static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        # Fallback to JSON if static files not available
        from fastapi.responses import JSONResponse
        return JSONResponse({
            "message": "Intelligent Resume Parser API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "web_interface": "/static/index.html",
            "note": "Static files not found. Check if static/index.html exists."
        })


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

