"""Database configuration and connection management."""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_timescaledb():
    """Initialize TimescaleDB extension and create hypertables."""
    from sqlalchemy import text
    
    # Only initialize TimescaleDB for PostgreSQL databases
    if not settings.database_url.startswith("sqlite"):
        with engine.connect() as conn:
            # Enable TimescaleDB extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            conn.commit()
            
            # Create hypertable for weather observations
            conn.execute(text("""
                SELECT create_hypertable('weather_observations', 'time', 
                                       if_not_exists => TRUE);
            """))
            conn.commit()
            
            # Set data retention policy (keep 1 year of data)
            conn.execute(text("""
                SELECT add_retention_policy('weather_observations', 
                                          INTERVAL '1 year',
                                          if_not_exists => TRUE);
            """))
            conn.commit()
            
            logger.info("TimescaleDB initialized successfully")
    else:
        logger.info("Skipping TimescaleDB initialization for SQLite database")
