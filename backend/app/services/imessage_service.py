"""iMessage integration service for AirPuff."""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
import httpx

from ..database import get_db
from ..models.user import User
from ..models.route import Route, RouteAirport, ScheduledMessage
from ..models.airport import Airport
from ..models.weather import WeatherObservation
from ..services.flirite_service import flirite_service

logger = logging.getLogger(__name__)


class iMessageService:
    """Service for handling iMessage integration with AirPuff."""
    
    def __init__(self):
        self.bridge_url = None  # Will be set from config
        self.api_key = None     # Will be set from config
        self.timeout = 30
        self.max_airports_per_request = 10  # Limit for on-demand requests
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send an iMessage to a recipient."""
        try:
            if not self.bridge_url or not self.api_key:
                logger.warning("iMessage bridge not configured, simulating message send")
                logger.info(f"Would send to {recipient}: {message}")
                return True
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "recipient": recipient,
                    "message": message,
                    "api_key": self.api_key
                }
                
                response = await client.post(f"{self.bridge_url}/send", json=payload)
                response.raise_for_status()
                
                logger.info(f"iMessage sent to {recipient}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending iMessage to {recipient}: {e}")
            return False
    
    async def process_incoming_message(self, sender: str, message: str) -> Optional[str]:
        """Process an incoming iMessage and return response."""
        try:
            # Clean and normalize the message
            message = message.strip().upper()
            
            # Check if it's a route request
            route_response = await self._handle_route_request(sender, message)
            if route_response:
                return route_response
            
            # Check if it's an airport list request
            airport_response = await self._handle_airport_request(sender, message)
            if airport_response:
                return airport_response
            
            # Check if it's a help request
            if message in ['HELP', '?', 'COMMANDS']:
                return self._get_help_message()
            
            # Check if it's a status request
            if message in ['STATUS', 'PING']:
                return self._get_status_message()
            
            # Unknown command
            return self._get_unknown_command_message()
            
        except Exception as e:
            logger.error(f"Error processing incoming message from {sender}: {e}")
            return "Error processing your request. Please try again."
    
    async def _handle_route_request(self, sender: str, message: str) -> Optional[str]:
        """Handle route-based weather requests."""
        # Look for route patterns like "route MyRoute" or "r MyRoute"
        route_patterns = [
            r'^ROUTE\s+(.+)$',
            r'^R\s+(.+)$',
            r'^ROUTE\s*$'  # Just "route" - get user's favorite route
        ]
        
        for pattern in route_patterns:
            match = re.match(pattern, message)
            if match:
                route_name = match.group(1) if match.groups() else None
                
                # Get user by phone number
                user = await self._get_user_by_phone(sender)
                if not user:
                    return "You're not registered with AirPuff. Please sign up at our website first."
                
                # Get route
                route = await self._get_user_route(user, route_name)
                if not route:
                    if route_name:
                        return f"Route '{route_name}' not found. Use 'ROUTES' to see your available routes."
                    else:
                        return "No favorite route set. Use 'ROUTES' to see your available routes."
                
                # Get weather for route airports
                weather_data = await self._get_route_weather(route)
                if not weather_data:
                    return f"No weather data available for route '{route.name}'."
                
                return self._format_route_response(route.name, weather_data)
        
        return None
    
    async def _handle_airport_request(self, sender: str, message: str) -> Optional[str]:
        """Handle airport list weather requests."""
        # Extract airport codes from message
        airport_codes = self._extract_airport_codes(message)
        
        if not airport_codes:
            return None
        
        # Limit number of airports
        if len(airport_codes) > self.max_airports_per_request:
            return f"Too many airports requested. Maximum {self.max_airports_per_request} airports per request."
        
        # Get weather for airports
        weather_data = await self._get_airports_weather(airport_codes)
        if not weather_data:
            return "No weather data available for the requested airports."
        
        return self._format_airport_response(weather_data)
    
    def _extract_airport_codes(self, message: str) -> List[str]:
        """Extract airport codes from a message."""
        # Pattern to match 3-4 letter airport codes
        airport_pattern = r'\b[A-Z]{3,4}\b'
        matches = re.findall(airport_pattern, message)
        
        # Filter out common words that might match the pattern
        exclude_words = {'THE', 'AND', 'FOR', 'YOU', 'ARE', 'BUT', 'NOT', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'MAN', 'MEN', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
        
        airport_codes = []
        for match in matches:
            if match not in exclude_words and len(match) >= 3:
                airport_codes.append(match)
        
        return airport_codes
    
    async def _get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number."""
        db = next(get_db())
        try:
            # In a real implementation, you'd have a phone field in the user table
            # For now, we'll use a simple mapping or return a demo user
            user = db.query(User).filter(User.email.like('%demo%')).first()
            return user
        finally:
            db.close()
    
    async def _get_user_route(self, user: User, route_name: Optional[str]) -> Optional[Route]:
        """Get user's route by name or favorite route."""
        db = next(get_db())
        try:
            if route_name:
                route = db.query(Route).filter(
                    Route.user_id == user.id,
                    Route.name.ilike(f"%{route_name}%")
                ).first()
            else:
                # Get favorite route
                route = db.query(Route).filter(
                    Route.user_id == user.id,
                    Route.is_favorite == True
                ).first()
            
            return route
        finally:
            db.close()
    
    async def _get_route_weather(self, route: Route) -> List[Dict[str, Any]]:
        """Get weather data for all airports in a route."""
        db = next(get_db())
        try:
            weather_data = []
            
            # Get route airports in order
            route_airports = db.query(RouteAirport).filter(
                RouteAirport.route_id == route.id
            ).order_by(RouteAirport.order).all()
            
            for ra in route_airports:
                airport = db.query(Airport).filter(Airport.id == ra.airport_id).first()
                if airport:
                    weather = await self._get_latest_weather(airport.icao)
                    if weather:
                        weather_data.append({
                            'airport': airport,
                            'weather': weather,
                            'order': ra.order,
                            'notes': ra.notes
                        })
            
            return weather_data
        finally:
            db.close()
    
    async def _get_airports_weather(self, airport_codes: List[str]) -> List[Dict[str, Any]]:
        """Get weather data for a list of airport codes."""
        db = next(get_db())
        try:
            weather_data = []
            
            for code in airport_codes:
                airport = db.query(Airport).filter(Airport.icao == code).first()
                if airport:
                    weather = await self._get_latest_weather(code)
                    if weather:
                        weather_data.append({
                            'airport': airport,
                            'weather': weather
                        })
                else:
                    # Try to fetch weather even if airport not in database
                    weather = await self._get_latest_weather(code)
                    if weather:
                        weather_data.append({
                            'airport': {'icao': code, 'name': f'{code} Airport'},
                            'weather': weather
                        })
            
            return weather_data
        finally:
            db.close()
    
    async def _get_latest_weather(self, icao: str) -> Optional[Dict[str, Any]]:
        """Get latest weather data for an airport."""
        try:
            # Try to get from database first
            db = next(get_db())
            try:
                # Get airport first to get airport_id
                airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
                if not airport:
                    return None
                
                observation = db.query(WeatherObservation).filter(
                    WeatherObservation.airport_id == airport.id
                ).order_by(WeatherObservation.time.desc()).first()
                
                if observation:
                    return {
                        'flight_category': observation.flight_category,
                        'temp_c': observation.temperature_c,
                        'dewpoint_c': observation.dewpoint_c,
                        'wind_dir_degrees': observation.wind_dir_deg,
                        'wind_speed_kt': observation.wind_speed_kts,
                        'visibility_mi': observation.visibility_mi,
                        'altimeter_in_hg': observation.altimeter_hg,
                        'sky_cover': observation.ceiling_code,
                        'raw_text': observation.raw_metar,
                        'observed_time': observation.time
                    }
            finally:
                db.close()
            
            # If no database data, try to fetch from Fli-Rite
            weather_data = await flirite_service.get_weather(icao)
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather for {icao}: {e}")
            return None
    
    def _format_route_response(self, route_name: str, weather_data: List[Dict[str, Any]]) -> str:
        """Format route weather response."""
        response = f"AirPuff Route: {route_name}\n"
        
        for item in weather_data:
            airport = item['airport']
            weather = item['weather']
            order = item.get('order', 0)
            notes = item.get('notes', '')
            
            line = self._format_weather_line(airport, weather)
            if notes:
                line += f" ({notes})"
            
            response += f"{order + 1}. {line}\n"
        
        return response.strip()
    
    def _format_airport_response(self, weather_data: List[Dict[str, Any]]) -> str:
        """Format airport list weather response."""
        response = "AirPuff:\n"
        
        for item in weather_data:
            airport = item['airport']
            weather = item['weather']
            
            line = self._format_weather_line(airport, weather)
            response += f"{line}\n"
        
        return response.strip()
    
    def _format_weather_line(self, airport: Dict[str, Any], weather: Dict[str, Any]) -> str:
        """Format a single weather line in the specified format."""
        icao = airport.get('icao', 'UNKN')
        flight_category = weather.get('flight_category', 'UNKN')
        altimeter = weather.get('altimeter_in_hg', 0)
        wind_dir = weather.get('wind_dir_degrees', 0)
        wind_speed = weather.get('wind_speed_kt', 0)
        visibility = weather.get('visibility_mi', 0)
        sky_cover = weather.get('sky_cover', 'UNKN')
        
        # Format wind
        if wind_speed == 0:
            wind_str = "Calm"
        else:
            wind_str = f"{wind_dir:03d}@{wind_speed}"
        
        # Format visibility
        if visibility >= 10:
            vis_str = "10.0mi"
        else:
            vis_str = f"{visibility:.1f}mi"
        
        # Format altimeter
        alt_str = f"{altimeter:.2f}"
        
        # Format sky cover and ceiling
        if sky_cover in ['CLR', 'SKC']:
            sky_str = "CLR|12000ft"
        elif sky_cover == 'FEW':
            sky_str = "FEW|3000ft"
        elif sky_cover == 'SCT':
            sky_str = "SCT|4000ft"
        elif sky_cover == 'BKN':
            sky_str = "BKN|2000ft"
        elif sky_cover == 'OVC':
            sky_str = "OVC|1000ft"
        else:
            sky_str = f"{sky_cover}|12000ft"
        
        return f"{icao}-{flight_category}-{alt_str}-{wind_str}-{vis_str}-{sky_str}"
    
    def _get_help_message(self) -> str:
        """Get help message for iMessage commands."""
        return """AirPuff iMessage Commands:

AIRPORT CODES: Send airport codes (e.g., KSFO KLAX KJFK)
ROUTE [name]: Get weather for a named route
ROUTES: List your available routes
STATUS: Check AirPuff service status
HELP: Show this help message

Examples:
• KSFO KLAX KJFK
• ROUTE MyCommute
• ROUTE (uses favorite route)

Maximum 10 airports per request."""
    
    def _get_status_message(self) -> str:
        """Get status message."""
        return f"AirPuff Status: Online\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\nService: Active"
    
    def _get_unknown_command_message(self) -> str:
        """Get message for unknown commands."""
        return "Unknown command. Send 'HELP' for available commands or airport codes for weather."
    
    async def send_scheduled_route_summary(self, scheduled_message: ScheduledMessage) -> bool:
        """Send a scheduled route summary."""
        try:
            db = next(get_db())
            try:
                # Get route and user
                route = db.query(Route).filter(Route.id == scheduled_message.route_id).first()
                user = db.query(User).filter(User.id == scheduled_message.user_id).first()
                
                if not route or not user:
                    logger.error(f"Route or user not found for scheduled message {scheduled_message.id}")
                    return False
                
                # Get weather data
                weather_data = await self._get_route_weather(route)
                if not weather_data:
                    logger.warning(f"No weather data for route {route.name}")
                    return False
                
                # Format message
                message = self._format_route_response(route.name, weather_data)
                
                # Send message
                success = await self.send_message(scheduled_message.recipient_imessage_id, message)
                
                if success:
                    # Update last_sent timestamp
                    scheduled_message.last_sent = datetime.now(timezone.utc)
                    db.commit()
                    logger.info(f"Scheduled message sent for route {route.name}")
                
                return success
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error sending scheduled route summary: {e}")
            return False
    
    async def process_scheduled_messages(self):
        """Process all due scheduled messages."""
        try:
            db = next(get_db())
            try:
                # Get active scheduled messages
                scheduled_messages = db.query(ScheduledMessage).filter(
                    ScheduledMessage.is_active == True
                ).all()
                
                for sm in scheduled_messages:
                    if self._should_send_message(sm):
                        await self.send_scheduled_route_summary(sm)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing scheduled messages: {e}")
    
    def _should_send_message(self, scheduled_message: ScheduledMessage) -> bool:
        """Check if a scheduled message should be sent."""
        now = datetime.now(timezone.utc)
        
        # Parse schedule_time (e.g., "daily 07:00", "hourly", "on-demand")
        schedule = scheduled_message.schedule_time.lower()
        
        if schedule == "on-demand":
            return False  # Don't auto-send on-demand messages
        
        if schedule.startswith("daily"):
            # Extract time (e.g., "daily 07:00")
            time_match = re.search(r'(\d{1,2}):(\d{2})', schedule)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                
                # Check if it's the right time and we haven't sent today
                if (now.hour == hour and now.minute == minute and 
                    (not scheduled_message.last_sent or 
                     scheduled_message.last_sent.date() < now.date())):
                    return True
        
        elif schedule == "hourly":
            # Send every hour if we haven't sent in the last hour
            if (not scheduled_message.last_sent or 
                now - scheduled_message.last_sent >= timedelta(hours=1)):
                return True
        
        return False


# Global iMessage service instance
imessage_service = iMessageService()
