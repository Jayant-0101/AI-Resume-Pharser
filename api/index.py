"""
Vercel Serverless Entry Point for AI Resume Parser
"""
import sys
import os
import traceback
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from app.main import app
except Exception as _import_err:
    # If app fails to import, create a minimal fallback app
    # that shows the actual error — helps debugging on Vercel
    import traceback as _tb
    _err_detail = _tb.format_exc()

    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.get("/{path:path}")
    @app.post("/{path:path}")
    async def startup_error(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "App failed to start",
                "detail": str(_import_err),
                "traceback": _err_detail[-2000:],  # last 2000 chars
                "python": sys.version,
            }
        )
