"""Weather API endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import get_db
from ...models.weather import WeatherObservation
from ...models.airport import Airport

router = APIRouter()


class WeatherResponse(BaseModel):
    """Weather observation response model."""
    time: datetime
    airport_id: int
    temperature_f: Optional[float]
    temperature_c: Optional[float]
    dewpoint_f: Optional[float]
    dewpoint_c: Optional[float]
    temp_dewpoint_spread_f: Optional[float]
    wind_dir_deg: Optional[int]
    wind_speed_kts: Optional[int]
    wind_speed_mph: Optional[float]
    wind_gust_kts: Optional[int]
    visibility_mi: Optional[float]
    visibility_m: Optional[float]
    ceiling_ft: Optional[int]
    ceiling_code: Optional[str]
    altimeter_hg: Optional[float]
    altimeter_mb: Optional[float]
    flight_category: Optional[str]
    raw_metar: Optional[str]
    metar_type: Optional[str]
    auto_station: Optional[str]
    wind_chill_f: Optional[float]
    heat_index_f: Optional[float]

    class Config:
        from_attributes = True


@router.get("/{icao}", response_model=WeatherResponse)
async def get_current_weather(icao: str, db: Session = Depends(get_db)):
    """Get current weather for an airport."""
    # Get airport
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Get latest weather observation
    weather = db.query(WeatherObservation).filter(
        WeatherObservation.airport_id == airport.id
    ).order_by(WeatherObservation.time.desc()).first()
    
    if not weather:
        raise HTTPException(status_code=404, detail="No weather data available")
    
    return weather


@router.get("/{icao}/history", response_model=List[WeatherResponse])
async def get_weather_history(
    icao: str,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: Session = Depends(get_db)
):
    """Get weather history for an airport."""
    # Get airport
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Get weather observations
    weather = db.query(WeatherObservation).filter(
        WeatherObservation.airport_id == airport.id,
        WeatherObservation.time >= start_time,
        WeatherObservation.time <= end_time
    ).order_by(WeatherObservation.time.desc()).all()
    
    return weather


@router.get("/", response_model=List[WeatherResponse])
async def get_multiple_weather(
    icaos: str = Query(..., description="Comma-separated list of ICAO codes"),
    db: Session = Depends(get_db)
):
    """Get current weather for multiple airports."""
    icao_list = [icao.strip().upper() for icao in icaos.split(",")]
    
    # Get airports
    airports = db.query(Airport).filter(Airport.icao.in_(icao_list)).all()
    airport_ids = [airport.id for airport in airports]
    
    if not airport_ids:
        raise HTTPException(status_code=404, detail="No airports found")
    
    # Get latest weather for each airport
    weather_observations = []
    for airport in airports:
        latest_weather = db.query(WeatherObservation).filter(
            WeatherObservation.airport_id == airport.id
        ).order_by(WeatherObservation.time.desc()).first()
        
        if latest_weather:
            weather_observations.append(latest_weather)
    
    return weather_observations
