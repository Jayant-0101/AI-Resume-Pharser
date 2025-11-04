"""
Logging configuration
"""
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure application logging"""
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

