"""Weather observation model for storing METAR data."""

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base


class WeatherObservation(Base):
    """Weather observation model for storing METAR data."""
    
    __tablename__ = "weather_observations"
    
    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    airport_id = Column(Integer, ForeignKey("airports.id"), primary_key=True, nullable=False)
    
    # Temperature data
    temperature_f = Column(Numeric(5, 2), nullable=True)
    temperature_c = Column(Numeric(5, 2), nullable=True)
    dewpoint_f = Column(Numeric(5, 2), nullable=True)
    dewpoint_c = Column(Numeric(5, 2), nullable=True)
    temp_dewpoint_spread_f = Column(Numeric(5, 2), nullable=True)
    
    # Wind data
    wind_dir_deg = Column(Integer, nullable=True)
    wind_speed_kts = Column(Integer, nullable=True)
    wind_speed_mph = Column(Numeric(5, 2), nullable=True)
    wind_gust_kts = Column(Integer, nullable=True)
    
    # Visibility and ceiling
    visibility_mi = Column(Numeric(5, 2), nullable=True)
    visibility_m = Column(Numeric(7, 2), nullable=True)
    ceiling_ft = Column(Integer, nullable=True)
    ceiling_code = Column(String(10), nullable=True)
    
    # Pressure
    altimeter_hg = Column(Numeric(5, 2), nullable=True)
    altimeter_mb = Column(Numeric(6, 2), nullable=True)
    
    # Flight category
    flight_category = Column(String(10), nullable=True)
    
    # Raw METAR
    raw_metar = Column(Text, nullable=True)
    
    # Additional data
    metar_type = Column(String(10), nullable=True)  # METAR, SPECI, etc.
    auto_station = Column(String(10), nullable=True)  # AUTO, COR, etc.
    wind_chill_f = Column(Numeric(5, 2), nullable=True)
    heat_index_f = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    airport = relationship("Airport", back_populates="weather_observations")
    
    def __repr__(self):
        return f"<WeatherObservation(airport_id={self.airport_id}, time={self.time}, category={self.flight_category})>"
