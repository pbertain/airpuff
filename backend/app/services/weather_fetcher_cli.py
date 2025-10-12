"""Command line interface for weather fetcher service."""

import asyncio
import logging
import sys
from sqlalchemy.orm import Session

from ..database import SessionLocal, init_timescaledb
from ..models.airport import Airport
from .weather_fetcher import WeatherFetcher
from .websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_weather_data():
    """Fetch weather data for all airports."""
    # Initialize database
    init_timescaledb()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get all airports
        airports = db.query(Airport).all()
        if not airports:
            logger.warning("No airports found in database")
            return
        
        airport_icaos = [airport.icao for airport in airports]
        logger.info(f"Fetching weather for {len(airport_icaos)} airports")
        
        # Fetch weather data
        async with WeatherFetcher() as fetcher:
            weather_data = await fetcher.fetch_weather_for_airports(airport_icaos)
            
            if weather_data:
                await fetcher.store_weather_data(weather_data, db)
                logger.info(f"Successfully stored {len(weather_data)} weather observations")
            else:
                logger.warning("No weather data received")
    
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(fetch_weather_data())
