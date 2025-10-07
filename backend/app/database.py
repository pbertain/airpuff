"""Database configuration and connection management."""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

# Create database engine
engine = create_engine(
    settings.timescaledb_url,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.timescaledb_url else {},
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


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
