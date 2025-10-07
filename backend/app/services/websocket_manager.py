"""WebSocket connection manager for real-time updates."""

from typing import List
from fastapi import WebSocket
import json


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        # Create a copy of the list to avoid modification during iteration
        connections_to_remove = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                connections_to_remove.append(connection)
        
        # Remove failed connections
        for connection in connections_to_remove:
            self.disconnect(connection)
    
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
