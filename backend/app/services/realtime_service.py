"""Real-time weather and notification service."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.weather import WeatherObservation
from ..models.airport import Airport
from ..models.route import Route, RouteAirport
from ..models.user import User
from .websocket_manager import ws_manager
from .flirite_service import flirite_service

logger = logging.getLogger(__name__)


class RealtimeService:
    """Service for managing real-time weather updates and notifications."""
    
    def __init__(self):
        self.is_running = False
        self.update_interval = 300  # 5 minutes
        self.last_update = {}
    
    async def start(self):
        """Start the real-time service."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting real-time weather service...")
        
        # Start the background task
        asyncio.create_task(self._weather_update_loop())
    
    async def stop(self):
        """Stop the real-time service."""
        self.is_running = False
        logger.info("Real-time weather service stopped.")
    
    async def _weather_update_loop(self):
        """Main loop for weather updates."""
        while self.is_running:
            try:
                await self._update_all_weather()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in weather update loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _update_all_weather(self):
        """Update weather for all airports and notify subscribers."""
        db = next(get_db())
        try:
            # Get all airports
            airports = db.query(Airport).all()
            
            for airport in airports:
                try:
                    # Fetch latest weather from Fli-Rite
                    weather_data = await flirite_service.get_weather(airport.icao)
                    
                    if weather_data:
                        # Store in database
                        await self._store_weather_observation(db, airport.icao, weather_data)
                        
                        # Notify WebSocket subscribers
                        await self._notify_weather_update(airport.icao, weather_data)
                        
                        # Check for route alerts
                        await self._check_route_alerts(db, airport.icao, weather_data)
                        
                        self.last_update[airport.icao] = datetime.now(timezone.utc)
                    
                except Exception as e:
                    logger.error(f"Error updating weather for {airport.icao}: {e}")
            
            logger.info(f"Weather update completed for {len(airports)} airports")
            
        finally:
            db.close()
    
    async def _store_weather_observation(self, db: Session, icao: str, weather_data: Dict[str, Any]):
        """Store weather observation in database."""
        try:
            # Parse weather data
            observation = WeatherObservation(
                icao_code=icao.upper(),
                observed_time=datetime.now(timezone.utc),
                flight_category=weather_data.get("flight_category"),
                temp_c=weather_data.get("temp_c"),
                dewpoint_c=weather_data.get("dewpoint_c"),
                wind_dir_degrees=weather_data.get("wind_dir_degrees"),
                wind_speed_kt=weather_data.get("wind_speed_kt"),
                visibility_mi=weather_data.get("visibility_mi"),
                altimeter_in_hg=weather_data.get("altimeter_in_hg"),
                sky_cover=weather_data.get("sky_cover"),
                raw_text=weather_data.get("raw_text")
            )
            
            db.add(observation)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing weather observation for {icao}: {e}")
            db.rollback()
    
    async def _notify_weather_update(self, icao: str, weather_data: Dict[str, Any]):
        """Notify WebSocket subscribers of weather update."""
        try:
            message = {
                "type": "weather_update",
                "airport": icao.upper(),
                "data": weather_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Send to airport-specific subscribers
            await ws_manager.send_to_airport_subscribers(icao.upper(), message)
            
            # Also broadcast to all connections (for general updates)
            await ws_manager.broadcast_json(message)
            
        except Exception as e:
            logger.error(f"Error notifying weather update for {icao}: {e}")
    
    async def _check_route_alerts(self, db: Session, icao: str, weather_data: Dict[str, Any]):
        """Check if weather conditions trigger route alerts."""
        try:
            # Get routes that include this airport
            route_airports = db.query(RouteAirport).join(Airport).filter(
                Airport.icao == icao.upper()
            ).all()
            
            for route_airport in route_airports:
                route = route_airport.route
                
                # Check if weather conditions warrant an alert
                alert_level = self._assess_weather_alert(weather_data)
                
                if alert_level > 0:
                    await self._send_route_alert(db, route, icao, weather_data, alert_level)
        
        except Exception as e:
            logger.error(f"Error checking route alerts for {icao}: {e}")
    
    def _assess_weather_alert(self, weather_data: Dict[str, Any]) -> int:
        """Assess weather conditions and return alert level (0-3)."""
        alert_level = 0
        
        # Check flight category
        flight_category = weather_data.get("flight_category", "").upper()
        if flight_category in ["LIFR", "IFR"]:
            alert_level = max(alert_level, 2)
        elif flight_category == "MVFR":
            alert_level = max(alert_level, 1)
        
        # Check visibility
        visibility = weather_data.get("visibility_mi")
        if visibility is not None:
            if visibility < 1:
                alert_level = max(alert_level, 3)
            elif visibility < 3:
                alert_level = max(alert_level, 2)
            elif visibility < 5:
                alert_level = max(alert_level, 1)
        
        # Check wind speed
        wind_speed = weather_data.get("wind_speed_kt")
        if wind_speed is not None:
            if wind_speed > 25:
                alert_level = max(alert_level, 2)
            elif wind_speed > 15:
                alert_level = max(alert_level, 1)
        
        return alert_level
    
    async def _send_route_alert(self, db: Session, route: Route, icao: str, weather_data: Dict[str, Any], alert_level: int):
        """Send route alert to user."""
        try:
            alert_message = {
                "type": "route_alert",
                "route_id": route.id,
                "route_name": route.name,
                "airport": icao.upper(),
                "alert_level": alert_level,
                "weather_data": weather_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": self._format_alert_message(route.name, icao, weather_data, alert_level)
            }
            
            # Send to user's WebSocket connections
            await ws_manager.send_to_user(route.user_id, alert_message)
            
            # Send to route subscribers
            await ws_manager.send_to_route_subscribers(route.id, alert_message)
            
            logger.info(f"Route alert sent for route {route.id} at {icao} (level {alert_level})")
            
        except Exception as e:
            logger.error(f"Error sending route alert: {e}")
    
    def _format_alert_message(self, route_name: str, icao: str, weather_data: Dict[str, Any], alert_level: int) -> str:
        """Format alert message for display."""
        level_names = {1: "CAUTION", 2: "WARNING", 3: "CRITICAL"}
        level_name = level_names.get(alert_level, "INFO")
        
        flight_category = weather_data.get("flight_category", "Unknown")
        visibility = weather_data.get("visibility_mi", "Unknown")
        wind_speed = weather_data.get("wind_speed_kt", "Unknown")
        
        return (
            f"{level_name} ALERT: Route '{route_name}' - {icao}\n"
            f"Flight Category: {flight_category}\n"
            f"Visibility: {visibility} SM\n"
            f"Wind Speed: {wind_speed} kts"
        )
    
    async def get_weather_for_airport(self, icao: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a specific airport."""
        try:
            weather_data = await flirite_service.get_weather(icao)
            if weather_data:
                await self._notify_weather_update(icao, weather_data)
            return weather_data
        except Exception as e:
            logger.error(f"Error getting weather for {icao}: {e}")
            return None
    
    async def subscribe_user_to_route(self, user_id: int, route_id: int):
        """Subscribe a user to route updates."""
        try:
            # Get user's WebSocket connections
            if user_id in ws_manager.user_connections:
                for websocket in ws_manager.user_connections[user_id]:
                    ws_manager.subscribe_to_route(websocket, route_id)
            
            logger.info(f"User {user_id} subscribed to route {route_id}")
            
        except Exception as e:
            logger.error(f"Error subscribing user to route: {e}")
    
    async def unsubscribe_user_from_route(self, user_id: int, route_id: int):
        """Unsubscribe a user from route updates."""
        try:
            # Get user's WebSocket connections
            if user_id in ws_manager.user_connections:
                for websocket in ws_manager.user_connections[user_id]:
                    ws_manager.unsubscribe_from_route(websocket, route_id)
            
            logger.info(f"User {user_id} unsubscribed from route {route_id}")
            
        except Exception as e:
            logger.error(f"Error unsubscribing user from route: {e}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get real-time service statistics."""
        return {
            "is_running": self.is_running,
            "update_interval": self.update_interval,
            "last_updates": len(self.last_update),
            "websocket_stats": ws_manager.get_connection_stats()
        }


# Global real-time service instance
realtime_service = RealtimeService()
