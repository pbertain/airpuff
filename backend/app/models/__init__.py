"""Database models exposed for metadata registration."""

from .admin import RouteTemplate, RouteTemplateAirport
from .airport import Airport
from .route import Route, RouteAirport, ScheduledMessage
from .user import User
from .weather import WeatherObservation

__all__ = [
    "Airport",
    "Route",
    "RouteAirport",
    "RouteTemplate",
    "RouteTemplateAirport",
    "ScheduledMessage",
    "User",
    "WeatherObservation",
]
