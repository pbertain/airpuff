"""Weather data fetching service."""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..config import settings
from ..models.airport import Airport
from ..models.weather import WeatherObservation
from .flight_category import calculate_flight_category
from .flirite_service import parse_fli_rite_response

logger = logging.getLogger(__name__)


class WeatherFetcher:
    """Service for fetching weather data from external APIs."""
    
    def __init__(self):
        self.fli_rite_url = (settings.fli_rite_base_url or "https://dev.fli-rite.net").rstrip("/") + "/api/metars"
        self.checkwx_url = "https://api.checkwx.com/metar"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_weather_for_airports(self, airport_icaos: List[str]) -> List[Dict]:
        """Fetch weather data for multiple airports."""
        if not self.session:
            raise RuntimeError("WeatherFetcher must be used as async context manager")
        
        weather_data = []
        
        # Try Fli-Rite first, fallback to CheckWX
        try:
            weather_data = await self._fetch_from_fli_rite(airport_icaos)
        except Exception as e:
            logger.warning(f"Fli-Rite API failed: {e}")
            try:
                weather_data = await self._fetch_from_checkwx(airport_icaos)
            except Exception as e2:
                logger.error(f"CheckWX API also failed: {e2}")
                raise
        
        return weather_data
    
    async def _fetch_from_fli_rite(self, airport_icaos: List[str]) -> List[Dict]:
        """Fetch weather data from Fli-Rite API."""
        icao_string = ",".join(airport_icaos)
        url = f"{self.fli_rite_url}/{icao_string}"
        
        headers = {
            "User-Agent": "AirPuff/2.0",
            "Accept": "application/json"
        }
        
        if settings.fli_rite_api_key:
            headers["Authorization"] = f"Bearer {settings.fli_rite_api_key}"
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Fli-Rite API returned status {response.status}")
            
            data = await response.json()
            return self._parse_fli_rite_response(data)
    
    async def _fetch_from_checkwx(self, airport_icaos: List[str]) -> List[Dict]:
        """Fetch weather data from CheckWX API."""
        icao_string = ",".join(airport_icaos)
        url = f"{self.checkwx_url}/{icao_string}/decoded"
        
        headers = {
            "X-API-Key": settings.checkwx_api_key or "",
            "User-Agent": "AirPuff/2.0"
        }
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"CheckWX API returned status {response.status}")
            
            data = await response.json()
            return self._parse_checkwx_response(data)
    
    def _parse_fli_rite_response(self, data: Dict) -> List[Dict]:
        """Parse Fli-Rite API response."""
        return parse_fli_rite_response(data)
    
    def _parse_checkwx_response(self, data: Dict) -> List[Dict]:
        """Parse CheckWX API response."""
        weather_data = []
        
        if "data" in data:
            for item in data["data"]:
                parsed = self._parse_metar_data(item)
                if parsed:
                    weather_data.append(parsed)
        
        return weather_data
    
    def _parse_metar_data(self, metar_data: Dict) -> Optional[Dict]:
        """Parse individual METAR data item."""
        try:
            # Extract basic information
            icao = metar_data.get("icao", "").upper()
            if not icao:
                return None
            
            # Parse observation time
            obs_time_str = metar_data.get("observed", "")
            if not obs_time_str:
                return None
            
            # Parse temperature
            temp_c = metar_data.get("temperature", {}).get("celsius")
            temp_f = metar_data.get("temperature", {}).get("fahrenheit")
            
            # Parse dewpoint
            dewpoint_c = metar_data.get("dewpoint", {}).get("celsius")
            dewpoint_f = metar_data.get("dewpoint", {}).get("fahrenheit")
            
            # Parse wind
            wind_dir = metar_data.get("wind", {}).get("degrees")
            wind_speed_kts = metar_data.get("wind", {}).get("speed_kts")
            wind_speed_mph = metar_data.get("wind", {}).get("speed_mph")
            
            # Parse visibility
            visibility_mi = metar_data.get("visibility", {}).get("miles")
            visibility_m = metar_data.get("visibility", {}).get("meters")
            
            # Parse ceiling
            ceiling_ft = metar_data.get("ceiling", {}).get("feet_agl")
            ceiling_code = metar_data.get("ceiling", {}).get("code")
            
            # Parse pressure
            altimeter_hg = metar_data.get("barometer", {}).get("hg")
            altimeter_mb = metar_data.get("barometer", {}).get("mb")
            
            # Parse flight category
            flight_category = metar_data.get("flight_category", "UNK")
            
            # Parse raw METAR
            raw_metar = metar_data.get("raw_text", "")
            
            # Calculate derived values
            temp_dewpoint_spread_f = None
            if temp_f is not None and dewpoint_f is not None:
                temp_dewpoint_spread_f = temp_f - dewpoint_f
            
            # Calculate wind chill
            wind_chill_f = None
            if temp_f is not None and wind_speed_mph is not None:
                if temp_f <= 50 and wind_speed_mph > 3:
                    wind_chill_f = 35.74 + (0.6215 * temp_f) - (35.75 * (wind_speed_mph ** 0.16)) + (0.4275 * temp_f * (wind_speed_mph ** 0.16))
            
            # Calculate flight category if not provided
            if flight_category == "UNK":
                flight_category = calculate_flight_category(
                    visibility_mi=visibility_mi,
                    ceiling_ft=ceiling_ft,
                    ceiling_code=ceiling_code
                )
            
            return {
                "icao": icao,
                "time": obs_time_str,
                "temperature_f": temp_f,
                "temperature_c": temp_c,
                "dewpoint_f": dewpoint_f,
                "dewpoint_c": dewpoint_c,
                "temp_dewpoint_spread_f": temp_dewpoint_spread_f,
                "wind_dir_deg": wind_dir,
                "wind_speed_kts": wind_speed_kts,
                "wind_speed_mph": wind_speed_mph,
                "visibility_mi": visibility_mi,
                "visibility_m": visibility_m,
                "ceiling_ft": ceiling_ft,
                "ceiling_code": ceiling_code,
                "altimeter_hg": altimeter_hg,
                "altimeter_mb": altimeter_mb,
                "flight_category": flight_category,
                "raw_metar": raw_metar,
                "wind_chill_f": wind_chill_f
            }
            
        except Exception as e:
            logger.error(f"Error parsing METAR data: {e}")
            return None
    
    async def store_weather_data(self, weather_data: List[Dict], db: Session):
        """Store weather data in the database."""
        for data in weather_data:
            try:
                # Get airport
                airport = db.query(Airport).filter(Airport.icao == data["icao"]).first()
                if not airport:
                    logger.warning(f"Airport {data['icao']} not found in database")
                    continue
                
                # Parse observation time
                obs_time = datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
                
                # Check if observation already exists
                existing = db.query(WeatherObservation).filter(
                    WeatherObservation.airport_id == airport.id,
                    WeatherObservation.time == obs_time
                ).first()
                
                if existing:
                    # Update existing observation
                    for key, value in data.items():
                        if key not in ["icao", "time"] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new observation
                    observation = WeatherObservation(
                        time=obs_time,
                        airport_id=airport.id,
                        temperature_f=data.get("temperature_f"),
                        temperature_c=data.get("temperature_c"),
                        dewpoint_f=data.get("dewpoint_f"),
                        dewpoint_c=data.get("dewpoint_c"),
                        temp_dewpoint_spread_f=data.get("temp_dewpoint_spread_f"),
                        wind_dir_deg=data.get("wind_dir_deg"),
                        wind_speed_kts=data.get("wind_speed_kts"),
                        wind_speed_mph=data.get("wind_speed_mph"),
                        visibility_mi=data.get("visibility_mi"),
                        visibility_m=data.get("visibility_m"),
                        ceiling_ft=data.get("ceiling_ft"),
                        ceiling_code=data.get("ceiling_code"),
                        altimeter_hg=data.get("altimeter_hg"),
                        altimeter_mb=data.get("altimeter_mb"),
                        flight_category=data.get("flight_category"),
                        raw_metar=data.get("raw_metar"),
                        wind_chill_f=data.get("wind_chill_f")
                    )
                    db.add(observation)
                
            except Exception as e:
                logger.error(f"Error storing weather data for {data.get('icao', 'unknown')}: {e}")
                continue
        
        db.commit()
        logger.info(f"Stored {len(weather_data)} weather observations")
