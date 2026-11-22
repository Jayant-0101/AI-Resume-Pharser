"""
Database configuration and session management
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def _create_engine():
    """Create SQLAlchemy engine with error handling"""
    url = settings.DATABASE_URL
    try:
        if url.startswith("sqlite"):
            eng = create_engine(url, connect_args={"check_same_thread": False})
        else:
            eng = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                connect_args={"connect_timeout": 10},
            )
        logger.info(f"Database engine created: {url[:30]}...")
        return eng
    except Exception as e:
        logger.error(f"Failed to create DB engine: {e}")
        # Fallback to in-memory SQLite so the app at least starts
        logger.warning("Falling back to in-memory SQLite (no data persistence)")
        return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


