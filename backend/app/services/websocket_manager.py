"""WebSocket connection manager for real-time updates."""

import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}  # user_id -> [websockets]
        self.airport_subscriptions: Dict[str, List[WebSocket]] = {}  # icao -> [websockets]
        self.route_subscriptions: Dict[int, List[WebSocket]] = {}  # route_id -> [websockets]
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from airport subscriptions
        for icao, connections in self.airport_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Remove from route subscriptions
        for route_id, connections in self.route_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def send_json_message(self, data: Dict[str, Any], websocket: WebSocket):
        """Send a JSON message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending JSON message: {e}")
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcast a JSON message to all connected clients."""
        message = json.dumps(data)
        await self.broadcast(message)
    
    async def send_to_user(self, user_id: int, data: Dict[str, Any]):
        """Send a message to all connections for a specific user."""
        if user_id not in self.user_connections:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, user_id)
    
    async def send_to_airport_subscribers(self, icao: str, data: Dict[str, Any]):
        """Send weather updates to subscribers of a specific airport."""
        if icao not in self.airport_subscriptions:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.airport_subscriptions[icao]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to airport {icao} subscribers: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_route_subscribers(self, route_id: int, data: Dict[str, Any]):
        """Send updates to subscribers of a specific route."""
        if route_id not in self.route_subscriptions:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.route_subscriptions[route_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to route {route_id} subscribers: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def subscribe_to_airport(self, websocket: WebSocket, icao: str):
        """Subscribe a WebSocket to updates for a specific airport."""
        if icao not in self.airport_subscriptions:
            self.airport_subscriptions[icao] = []
        
        if websocket not in self.airport_subscriptions[icao]:
            self.airport_subscriptions[icao].append(websocket)
            logger.info(f"WebSocket subscribed to airport {icao}")
    
    def subscribe_to_route(self, websocket: WebSocket, route_id: int):
        """Subscribe a WebSocket to updates for a specific route."""
        if route_id not in self.route_subscriptions:
            self.route_subscriptions[route_id] = []
        
        if websocket not in self.route_subscriptions[route_id]:
            self.route_subscriptions[route_id].append(websocket)
            logger.info(f"WebSocket subscribed to route {route_id}")
    
    def unsubscribe_from_airport(self, websocket: WebSocket, icao: str):
        """Unsubscribe a WebSocket from updates for a specific airport."""
        if icao in self.airport_subscriptions:
            if websocket in self.airport_subscriptions[icao]:
                self.airport_subscriptions[icao].remove(websocket)
                logger.info(f"WebSocket unsubscribed from airport {icao}")
    
    def unsubscribe_from_route(self, websocket: WebSocket, route_id: int):
        """Unsubscribe a WebSocket from updates for a specific route."""
        if route_id in self.route_subscriptions:
            if websocket in self.route_subscriptions[route_id]:
                self.route_subscriptions[route_id].remove(websocket)
                logger.info(f"WebSocket unsubscribed from route {route_id}")
    
    async def handle_message(self, websocket: WebSocket, message: str, user_id: Optional[int] = None):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe_airport":
                icao = data.get("icao")
                if icao:
                    self.subscribe_to_airport(websocket, icao.upper())
                    await self.send_json_message({
                        "type": "subscription_confirmed",
                        "airport": icao.upper(),
                        "message": f"Subscribed to weather updates for {icao.upper()}"
                    }, websocket)
            
            elif message_type == "subscribe_route":
                route_id = data.get("route_id")
                if route_id:
                    self.subscribe_to_route(websocket, route_id)
                    await self.send_json_message({
                        "type": "subscription_confirmed",
                        "route_id": route_id,
                        "message": f"Subscribed to updates for route {route_id}"
                    }, websocket)
            
            elif message_type == "unsubscribe_airport":
                icao = data.get("icao")
                if icao:
                    self.unsubscribe_from_airport(websocket, icao.upper())
                    await self.send_json_message({
                        "type": "unsubscription_confirmed",
                        "airport": icao.upper(),
                        "message": f"Unsubscribed from weather updates for {icao.upper()}"
                    }, websocket)
            
            elif message_type == "unsubscribe_route":
                route_id = data.get("route_id")
                if route_id:
                    self.unsubscribe_from_route(websocket, route_id)
                    await self.send_json_message({
                        "type": "unsubscription_confirmed",
                        "route_id": route_id,
                        "message": f"Unsubscribed from updates for route {route_id}"
                    }, websocket)
            
            elif message_type == "ping":
                await self.send_json_message({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, websocket)
            
            else:
                await self.send_json_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)
        
        except json.JSONDecodeError:
            await self.send_json_message({
                "type": "error",
                "message": "Invalid JSON format"
            }, websocket)
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_json_message({
                "type": "error",
                "message": "Internal server error"
            }, websocket)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        return {
            "total_connections": len(self.active_connections),
            "user_connections": len(self.user_connections),
            "airport_subscriptions": len(self.airport_subscriptions),
            "route_subscriptions": len(self.route_subscriptions),
            "subscribed_airports": list(self.airport_subscriptions.keys()),
            "subscribed_routes": list(self.route_subscriptions.keys())
        }
    
    # Legacy methods for backward compatibility
    async def broadcast_weather_update(self, airport_icao: str, weather_data: dict):
        """Broadcast weather update to all connected clients."""
        message = {
            "type": "weather_update",
            "airport": airport_icao,
            "data": weather_data,
            "timestamp": weather_data.get("time")
        }
        
        await self.broadcast(json.dumps(message))


    async def broadcast_airport_list_update(self, airports: List[dict]):
        """Broadcast airport list update to all connected clients."""
        message = {
            "type": "airport_list_update",
            "airports": airports,
            "timestamp": None
        }
        
        await self.broadcast(json.dumps(message))


# Global WebSocket manager instance
ws_manager = WebSocketManager()
