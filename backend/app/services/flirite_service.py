"""Fli-Rite API service for weather data."""

import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class FliRiteService:
    """Service for fetching weather data from Fli-Rite API."""
    
    def __init__(self):
        self.base_url = "https://api.fli-rite.net"
        self.api_key = None  # Will be set from config
        self.timeout = 30
    
    async def get_weather(self, icao: str) -> Optional[Dict[str, Any]]:
        """Get weather data for an airport."""
        try:
            # For now, return mock data
            # In production, this would call the actual Fli-Rite API
            return self._get_mock_weather(icao)
        except Exception as e:
            logger.error(f"Error fetching weather for {icao}: {e}")
            return None
    
    def _get_mock_weather(self, icao: str) -> Dict[str, Any]:
        """Generate mock weather data for testing."""
        import random
        from datetime import datetime, timezone
        
        # Mock weather conditions
        conditions = [
            {"flight_category": "VFR", "visibility_mi": 10.0, "wind_speed_kt": 8},
            {"flight_category": "MVFR", "visibility_mi": 4.0, "wind_speed_kt": 12},
            {"flight_category": "IFR", "visibility_mi": 2.0, "wind_speed_kt": 18},
            {"flight_category": "LIFR", "visibility_mi": 0.5, "wind_speed_kt": 25}
        ]
        
        condition = random.choice(conditions)
        
        return {
            "icao": icao.upper(),
            "flight_category": condition["flight_category"],
            "temp_c": round(random.uniform(-10, 30), 1),
            "dewpoint_c": round(random.uniform(-15, 25), 1),
            "wind_dir_degrees": random.randint(0, 360),
            "wind_speed_kt": condition["wind_speed_kt"],
            "visibility_mi": condition["visibility_mi"],
            "altimeter_in_hg": round(random.uniform(29.50, 30.50), 2),
            "sky_cover": random.choice(["CLR", "FEW", "SCT", "BKN", "OVC"]),
            "raw_text": f"{icao.upper()} {datetime.now(timezone.utc).strftime('%d%H%M')}Z AUTO {condition['flight_category']} {condition['visibility_mi']}SM",
            "time": datetime.now(timezone.utc).isoformat()
        }


# Global Fli-Rite service instance
flirite_service = FliRiteService()
