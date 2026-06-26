"""Fli-Rite API service for weather data."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


def parse_metar_data(metar_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize a single Fli-Rite METAR payload into AirPuff's weather shape."""

    try:
        icao = (metar_data.get("icao") or metar_data.get("station") or "").upper()
        if not icao:
            return None

        observed = metar_data.get("observed") or metar_data.get("time") or metar_data.get("observed_time")
        if not observed:
            observed = datetime.now(timezone.utc).isoformat()

        temperature = metar_data.get("temperature", {})
        dewpoint = metar_data.get("dewpoint", {})
        wind = metar_data.get("wind", {})
        visibility = metar_data.get("visibility", {})
        ceiling = metar_data.get("ceiling", {})
        barometer = metar_data.get("barometer", {})

        temp_c = metar_data.get("temp_c", temperature.get("celsius"))
        temp_f = metar_data.get("temp_f", temperature.get("fahrenheit"))
        dewpoint_c = metar_data.get("dewpoint_c", dewpoint.get("celsius"))
        dewpoint_f = metar_data.get("dewpoint_f", dewpoint.get("fahrenheit"))
        wind_dir = metar_data.get("wind_dir_degrees", wind.get("degrees"))
        wind_speed_kts = metar_data.get("wind_speed_kt", wind.get("speed_kts"))
        wind_speed_mph = metar_data.get("wind_speed_mph", wind.get("speed_mph"))
        visibility_mi = metar_data.get("visibility_mi", visibility.get("miles"))
        visibility_m = metar_data.get("visibility_m", visibility.get("meters"))
        ceiling_ft = metar_data.get("ceiling_ft", ceiling.get("feet_agl"))
        ceiling_code = metar_data.get("ceiling_code", ceiling.get("code"))
        altimeter_hg = metar_data.get("altimeter_in_hg", barometer.get("hg"))
        altimeter_mb = metar_data.get("altimeter_mb", barometer.get("mb"))
        flight_category = metar_data.get("flight_category", "UNK")
        raw_metar = metar_data.get("raw_text", "")

        temp_dewpoint_spread_f = None
        if temp_f is not None and dewpoint_f is not None:
            temp_dewpoint_spread_f = temp_f - dewpoint_f

        return {
            "icao": icao,
            "time": observed,
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
            "wind_chill_f": metar_data.get("wind_chill_f"),
            "temp_c": temp_c,
            "dewpoint_c": dewpoint_c,
            "wind_dir_degrees": wind_dir,
            "wind_speed_kt": wind_speed_kts,
            "altimeter_in_hg": altimeter_hg,
            "sky_cover": metar_data.get("sky_cover", ceiling_code),
            "raw_text": raw_metar,
            "observed_time": observed,
        }
    except Exception as e:
        logger.error(f"Error parsing Fli-Rite METAR payload: {e}")
        return None


def parse_fli_rite_response(data: Any) -> List[Dict[str, Any]]:
    """Parse a Fli-Rite API response into normalized weather records."""

    items: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            items = data["data"]
        elif any(key in data for key in ("icao", "station", "flight_category", "raw_text")):
            items = [data]
    elif isinstance(data, list):
        items = data

    parsed: List[Dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            metar = parse_metar_data(item)
            if metar:
                parsed.append(metar)
    return parsed


class FliRiteService:
    """Service for fetching weather data from Fli-Rite API."""

    def __init__(self):
        self.base_url = (settings.fli_rite_base_url or "https://dev.fli-rite.net").rstrip("/")
        self.api_key = settings.fli_rite_api_key
        self.timeout = 30

    async def get_weather(self, icao: str) -> Optional[Dict[str, Any]]:
        """Get current weather data for an airport."""
        try:
            response = await self._fetch_weather([icao])
            return response[0] if response else None
        except Exception as e:
            logger.error(f"Error fetching weather for {icao}: {e}")
            return None

    async def _fetch_weather(self, airport_icaos: List[str]) -> List[Dict[str, Any]]:
        """Fetch weather data for one or more airports from Fli-Rite."""

        icao_string = ",".join(code.upper() for code in airport_icaos)
        url = f"{self.base_url}/api/metars/{icao_string}"
        headers = {
            "User-Agent": "AirPuff/2.0",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return parse_fli_rite_response(response.json())


# Global Fli-Rite service instance
flirite_service = FliRiteService()
