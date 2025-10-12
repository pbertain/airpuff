"""WebSocket API endpoints for real-time features."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...models.route import Route
from ...api.v1.auth import get_current_user
from ...services.websocket_manager import ws_manager
from ...services.realtime_service import realtime_service

router = APIRouter()


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "websocket_stats": ws_manager.get_connection_stats(),
        "realtime_service_stats": realtime_service.get_service_stats()
    }


@router.post("/subscribe/airport/{icao}")
async def subscribe_to_airport(
    icao: str,
    current_user: User = Depends(get_current_user)
):
    """Subscribe user to airport weather updates."""
    try:
        # This would typically be handled through WebSocket messages
        # But we can also provide REST endpoints for convenience
        return {
            "message": f"Subscribed to weather updates for {icao.upper()}",
            "airport": icao.upper(),
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscribe/route/{route_id}")
async def subscribe_to_route(
    route_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe user to route updates."""
    try:
        # Verify route exists and belongs to user
        route = db.query(Route).filter(
            Route.id == route_id,
            Route.user_id == current_user.id
        ).first()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        await realtime_service.subscribe_user_to_route(current_user.id, route_id)
        
        return {
            "message": f"Subscribed to updates for route '{route.name}'",
            "route_id": route_id,
            "route_name": route.name,
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unsubscribe/route/{route_id}")
async def unsubscribe_from_route(
    route_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe user from route updates."""
    try:
        # Verify route exists and belongs to user
        route = db.query(Route).filter(
            Route.id == route_id,
            Route.user_id == current_user.id
        ).first()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        await realtime_service.unsubscribe_user_from_route(current_user.id, route_id)
        
        return {
            "message": f"Unsubscribed from updates for route '{route.name}'",
            "route_id": route_id,
            "route_name": route.name,
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/weather/refresh/{icao}")
async def refresh_weather(icao: str):
    """Manually refresh weather for an airport."""
    try:
        weather_data = await realtime_service.get_weather_for_airport(icao.upper())
        
        if weather_data:
            return {
                "message": f"Weather refreshed for {icao.upper()}",
                "airport": icao.upper(),
                "weather_data": weather_data
            }
        else:
            raise HTTPException(status_code=404, detail=f"No weather data available for {icao.upper()}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/service/start")
async def start_realtime_service():
    """Start the real-time weather service."""
    try:
        await realtime_service.start()
        return {
            "message": "Real-time service started",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/service/stop")
async def stop_realtime_service():
    """Stop the real-time weather service."""
    try:
        await realtime_service.stop()
        return {
            "message": "Real-time service stopped",
            "status": "stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
