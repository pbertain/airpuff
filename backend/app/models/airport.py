"""Airport model for storing airport information."""

from sqlalchemy import Boolean, Column, Integer, Numeric, String
from sqlalchemy.orm import relationship
from ..database import Base


class Airport(Base):
    """Airport model representing airport information."""
    
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    icao = Column(String(4), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    elevation_ft = Column(Integer, nullable=True)
    atis_phone = Column(String(20), nullable=True)
    tower_phone = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    is_monitored = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    weather_observations = relationship("WeatherObservation", back_populates="airport")
    route_airports = relationship("RouteAirport", back_populates="airport")
    
    def __repr__(self):
        return f"<Airport(icao='{self.icao}', name='{self.name}')>"
