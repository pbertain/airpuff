"""cURL-friendly weather endpoints with clear-text output."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ....database import get_db
from ....models.weather import WeatherObservation
from ....models.airport import Airport
from ....services.flirite_service import flirite_service

router = APIRouter()


def format_weather_text(weather: WeatherObservation, airport: Airport) -> str:
    """Format weather data as clear text."""
    lines = [
        f"Airport: {airport.icao} - {airport.name or 'Unknown'}",
        f"Observation Time: {weather.time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Raw METAR: {weather.raw_metar or 'N/A'}",
        "",
        "Current Conditions:",
        f"  Flight Category: {weather.flight_category or 'UNK'}",
        f"  Temperature: {weather.temperature_f or 'N/A'}°F ({weather.temperature_c or 'N/A'}°C)",
        f"  Dewpoint: {weather.dewpoint_f or 'N/A'}°F ({weather.dewpoint_c or 'N/A'}°C)",
        f"  Temp-Dewpoint Spread: {weather.temp_dewpoint_spread_f or 'N/A'}°F",
        f"  Wind: {weather.wind_dir_deg or 'N/A'}° @ {weather.wind_speed_kts or 'N/A'} kts ({weather.wind_speed_mph or 'N/A'} mph)",
        f"  Wind Gust: {weather.wind_gust_kts or 'N/A'} kts",
        f"  Visibility: {weather.visibility_mi or 'N/A'} SM ({weather.visibility_m or 'N/A'} m)",
        f"  Ceiling: {weather.ceiling_ft or 'N/A'} ft AGL ({weather.ceiling_code or 'N/A'})",
        f"  Altimeter: {weather.altimeter_hg or 'N/A'}\" Hg ({weather.altimeter_mb or 'N/A'} mb)",
        f"  Wind Chill: {weather.wind_chill_f or 'N/A'}°F",
        f"  Heat Index: {weather.heat_index_f or 'N/A'}°F",
        f"  METAR Type: {weather.metar_type or 'N/A'}",
        f"  Auto Station: {weather.auto_station or 'N/A'}",
        "---"
    ]
    return "\n".join(lines)


def format_weather_summary(weather: WeatherObservation, airport: Airport) -> str:
    """Format weather data as a brief summary."""
    return f"{airport.icao}: {weather.flight_category or 'UNK'} | {weather.temperature_f or '--'}°F | {weather.wind_dir_deg or '--'}°@{weather.wind_speed_kts or '--'}kt | {weather.visibility_mi or '--'}SM | {weather.ceiling_ft or '--'}ft"


def format_live_weather_summary(weather: dict, airport: Optional[Airport]) -> str:
    """Format live Fli-Rite weather data as a brief summary."""
    airport_code = (airport.icao if airport else weather.get("icao") or "UNK").upper()
    return (
        f"{airport_code}: {weather.get('flight_category') or 'UNK'} | "
        f"{weather.get('temperature_f') or weather.get('temp_f') or '--'}°F | "
        f"{weather.get('wind_dir_deg') or weather.get('wind_dir_degrees') or '--'}@"
        f"{weather.get('wind_speed_kts') or weather.get('wind_speed_kt') or '--'}kt | "
        f"{weather.get('visibility_mi') or '--'}SM | "
        f"{weather.get('ceiling_ft') or '--'}ft"
    )


@router.get("/{icao}", response_class=Response)
async def get_current_weather_curl(icao: str, db: Session = Depends(get_db)):
    """Get current weather for an airport in clear text format."""
    # Get airport
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()

    if airport:
        # Get latest weather observation
        weather = db.query(WeatherObservation).filter(
            WeatherObservation.airport_id == airport.id
        ).order_by(WeatherObservation.time.desc()).first()

        if weather:
            return Response(content=format_weather_text(weather, airport), media_type="text/plain")

    live_weather = await flirite_service.get_weather(icao.upper())
    if live_weather:
        airport_name = airport.name if airport and airport.name else "Unknown"
        lines = [
            f"Airport: {icao.upper()} - {airport_name}",
            f"Observation Time: {live_weather.get('time') or live_weather.get('observed_time') or 'N/A'}",
            f"Raw METAR: {live_weather.get('raw_metar') or live_weather.get('raw_text') or 'N/A'}",
            "",
            "Current Conditions:",
            f"  Flight Category: {live_weather.get('flight_category') or 'UNK'}",
            f"  Temperature: {live_weather.get('temperature_f') or live_weather.get('temp_f') or 'N/A'}°F ({live_weather.get('temperature_c') or live_weather.get('temp_c') or 'N/A'}°C)",
            f"  Dewpoint: {live_weather.get('dewpoint_f') or 'N/A'}°F ({live_weather.get('dewpoint_c') or 'N/A'}°C)",
            f"  Temp-Dewpoint Spread: {live_weather.get('temp_dewpoint_spread_f') or 'N/A'}°F",
            f"  Wind: {live_weather.get('wind_dir_deg') or live_weather.get('wind_dir_degrees') or 'N/A'}° @ {live_weather.get('wind_speed_kts') or live_weather.get('wind_speed_kt') or 'N/A'} kts",
            f"  Visibility: {live_weather.get('visibility_mi') or 'N/A'} SM ({live_weather.get('visibility_m') or 'N/A'} m)",
            f"  Ceiling: {live_weather.get('ceiling_ft') or 'N/A'} ft AGL ({live_weather.get('ceiling_code') or 'N/A'})",
            f"  Altimeter: {live_weather.get('altimeter_hg') or live_weather.get('altimeter_in_hg') or 'N/A'}\" Hg ({live_weather.get('altimeter_mb') or 'N/A'} mb)",
            f"  Wind Chill: {live_weather.get('wind_chill_f') or 'N/A'}°F",
            f"  Sky Cover: {live_weather.get('sky_cover') or 'N/A'}",
            "---",
        ]
        return Response(content="\n".join(lines), media_type="text/plain")

    if not airport:
        return Response(content=f"Airport {icao.upper()} not found.\n", media_type="text/plain", status_code=404)

    return Response(content=f"No weather data available for {icao.upper()}.\n", media_type="text/plain", status_code=404)


@router.get("/{icao}/history", response_class=Response)
async def get_weather_history_curl(
    icao: str,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: Session = Depends(get_db)
):
    """Get weather history for an airport in clear text format."""
    # Get airport
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        return Response(content=f"Airport {icao.upper()} not found.\n", media_type="text/plain", status_code=404)
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Get weather observations
    weather_obs = db.query(WeatherObservation).filter(
        WeatherObservation.airport_id == airport.id,
        WeatherObservation.time >= start_time,
        WeatherObservation.time <= end_time
    ).order_by(WeatherObservation.time.desc()).all()
    
    if not weather_obs:
        return Response(content=f"No weather history available for {icao.upper()} in the last {hours} hours.\n", media_type="text/plain", status_code=404)
    
    output_lines = [
        f"Weather History for {airport.icao} - {airport.name or 'Unknown'}",
        f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} UTC",
        f"Found {len(weather_obs)} observations:\n"
    ]
    
    for i, weather in enumerate(weather_obs, 1):
        output_lines.append(f"{i}. {weather.time.strftime('%m/%d %H:%M')} - {weather.flight_category or 'UNK'} | {weather.temperature_f or '--'}°F | {weather.wind_dir_deg or '--'}°@{weather.wind_speed_kts or '--'}kt | {weather.visibility_mi or '--'}SM")
    
    return Response(content="\n".join(output_lines), media_type="text/plain")


@router.get("/", response_class=Response)
async def get_multiple_weather_curl(
    icaos: str = Query(..., description="Comma-separated list of ICAO codes"),
    db: Session = Depends(get_db)
):
    """Get current weather for multiple airports in clear text format."""
    icao_list = [icao.strip().upper() for icao in icaos.split(",")]
    
    # Get airports
    airports = db.query(Airport).filter(Airport.icao.in_(icao_list)).all()
    airport_dict = {airport.icao: airport for airport in airports}
    
    if not airports:
        return Response(content="No airports found.\n", media_type="text/plain", status_code=404)
    
    output_lines = [f"Weather Summary for {len(airports)} airports:\n"]
    
    for icao in icao_list:
        airport = airport_dict.get(icao)
        if not airport:
            output_lines.append(f"{icao}: Airport not found")
            continue
        
        # Get latest weather
        weather = db.query(WeatherObservation).filter(
            WeatherObservation.airport_id == airport.id
        ).order_by(WeatherObservation.time.desc()).first()
        
        if weather:
            output_lines.append(format_weather_summary(weather, airport))
        else:
            live_weather = await flirite_service.get_weather(icao)
            if live_weather:
                output_lines.append(format_live_weather_summary(live_weather, airport))
            else:
                output_lines.append(f"{icao}: No weather data available")
    
    return Response(content="\n".join(output_lines), media_type="text/plain")
