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
    _err_detail = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def startup_error(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "App failed to start",
                "detail": str(_import_err),
                "traceback": _err_detail[-3000:],
                "python": sys.version,
            }
        )

# Vercel needs 'app' at module level — it's always assigned above (either real or fallback)
