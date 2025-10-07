"""Route models for user-defined flight routes."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base

# Association table for route-airport many-to-many relationship
route_airports = Table(
    'route_airports',
    Base.metadata,
    Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
    Column('airport_id', Integer, ForeignKey('airports.id'), primary_key=True),
    Column('order', Integer, nullable=False)  # Order of airports in route
)


class Route(Base):
    """Route model for user-defined flight routes."""
    
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Route settings
    is_public = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="routes")
    airports = relationship("Airport", secondary=route_airports, back_populates="route_airports")
    scheduled_messages = relationship("ScheduledMessage", back_populates="route")
    
    def __repr__(self):
        return f"<Route(name='{self.name}', user_id={self.user_id})>"


class RouteAirport(Base):
    """Association model for route-airport relationships with additional data."""
    
    __tablename__ = "route_airport_details"
    
    route_id = Column(Integer, ForeignKey("routes.id"), primary_key=True)
    airport_id = Column(Integer, ForeignKey("airports.id"), primary_key=True)
    order = Column(Integer, nullable=False)
    
    # Additional route-specific airport data
    notes = Column(Text, nullable=True)
    is_waypoint = Column(Boolean, default=False)  # True for waypoints, False for destinations
    
    # Relationships
    route = relationship("Route")
    airport = relationship("Airport", back_populates="route_airports")
    
    def __repr__(self):
        return f"<RouteAirport(route_id={self.route_id}, airport_id={self.airport_id}, order={self.order})>"


class ScheduledMessage(Base):
    """Scheduled message model for iMessage/SMS notifications."""
    
    __tablename__ = "scheduled_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    
    # Message settings
    name = Column(String(255), nullable=False)
    message_type = Column(String(20), nullable=False)  # imessage, sms
    phone_number = Column(String(20), nullable=False)
    
    # Scheduling
    schedule_type = Column(String(20), nullable=False)  # daily, weekly, on_demand
    schedule_time = Column(String(10), nullable=True)  # HH:MM format
    schedule_days = Column(String(20), nullable=True)  # mon,tue,wed,etc or daily
    
    # Message content
    message_template = Column(Text, nullable=True)
    include_forecast = Column(Boolean, default=False)
    max_airports = Column(Integer, default=5)  # For SMS character limits
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sent = Column(TIMESTAMP(timezone=True), nullable=True)
    next_send = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="scheduled_messages")
    route = relationship("Route", back_populates="scheduled_messages")
    
    def __repr__(self):
        return f"<ScheduledMessage(name='{self.name}', type='{self.message_type}', phone='{self.phone_number}')>"
