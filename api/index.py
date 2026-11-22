"""
Vercel Serverless Entry Point for AI Resume Parser
"""
import sys
import traceback
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Define app at TOP LEVEL unconditionally so Vercel's static scanner finds it
from fastapi import FastAPI
app = FastAPI()  # Vercel requires this to be a plain top-level assignment

# Now try to load the real app (overwrites placeholder above if successful)
try:
    from app.main import app  # noqa: F811 — intentional overwrite
except Exception as _boot_err:
    _boot_tb = traceback.format_exc()

    # Real app failed to load — attach error route to placeholder app
    from fastapi.responses import JSONResponse

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def _boot_error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "App failed to start — import error",
                "detail": str(_boot_err),
                "traceback": _boot_tb[-3000:],
                "python": sys.version,
            }
        )
