# Pytest Configuration for AirPuff

import pytest
import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

# Test database URL
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/airpuff_test")

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_airport():
    """Sample airport data for testing."""
    return {
        "icao": "KSFO",
        "name": "San Francisco International Airport",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "latitude": 37.6213,
        "longitude": -122.3790,
        "elevation_ft": 13
    }

@pytest.fixture(scope="function")
def sample_weather():
    """Sample weather data for testing."""
    return {
        "airport_id": 1,
        "time": "2024-01-01T12:00:00Z",
        "flight_category": "VFR",
        "temperature_c": 20.0,
        "dewpoint_c": 15.0,
        "wind_dir_deg": 270,
        "wind_speed_kts": 10,
        "visibility_mi": 10.0,
        "altimeter_hg": 29.92,
        "ceiling_code": "CLR",
        "raw_metar": "KSFO 011200Z 27010KT 10SM CLR 20/15 A2992"
    }

@pytest.fixture(scope="function")
def sample_user():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True
    }
