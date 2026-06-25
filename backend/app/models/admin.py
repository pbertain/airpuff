"""Admin-managed models for monitored airports and route templates."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from ..database import Base


class RouteTemplate(Base):
    """Reusable route template managed by admins."""

    __tablename__ = "route_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    airports = relationship(
        "RouteTemplateAirport",
        back_populates="route_template",
        cascade="all, delete-orphan",
        order_by="RouteTemplateAirport.order",
    )

    def __repr__(self):
        return f"<RouteTemplate(name='{self.name}', active={self.is_active})>"


class RouteTemplateAirport(Base):
    """Ordered airports within a route template."""

    __tablename__ = "route_template_airports"

    route_template_id = Column(
        Integer,
        ForeignKey("route_templates.id"),
        primary_key=True,
    )
    airport_id = Column(Integer, ForeignKey("airports.id"), primary_key=True)
    order = Column(Integer, nullable=False)

    route_template = relationship("RouteTemplate", back_populates="airports")
    airport = relationship("Airport")

    def __repr__(self):
        return (
            f"<RouteTemplateAirport(route_template_id={self.route_template_id}, "
            f"airport_id={self.airport_id}, order={self.order})>"
        )
