"""User model for authentication and user management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # OAuth provider info
    provider = Column(String(50), nullable=False)  # google, apple, keycloak
    provider_id = Column(String(255), nullable=False)
    
    # User preferences
    units = Column(String(10), default="imperial")  # imperial, metric
    default_airports = Column(Text, nullable=True)  # JSON array of ICAO codes
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # API access
    api_key = Column(String(64), unique=True, nullable=True, index=True)
    
    # Relationships
    routes = relationship("Route", back_populates="user")
    scheduled_messages = relationship("ScheduledMessage", back_populates="user")
    
    def __repr__(self):
        return f"<User(email='{self.email}', provider='{self.provider}')>"
