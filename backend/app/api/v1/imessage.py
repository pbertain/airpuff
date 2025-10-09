"""iMessage API endpoints for AirPuff."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from ...database import get_db
from ...models.user import User
from ...models.route import Route, ScheduledMessage
from ...api.v1.auth import get_current_user
from ...services.imessage_service import imessage_service

router = APIRouter()


class iMessageRequest(BaseModel):
    """iMessage request model."""
    sender: str
    message: str


class iMessageResponse(BaseModel):
    """iMessage response model."""
    response: str
    processed: bool
    timestamp: datetime


class ScheduledMessageCreate(BaseModel):
    """Scheduled message creation model."""
    route_id: int
    schedule_time: str  # e.g., "daily 07:00", "hourly", "on-demand"
    recipient_imessage_id: str
    is_active: bool = True


class ScheduledMessageResponse(BaseModel):
    """Scheduled message response model."""
    id: int
    route_id: int
    user_id: int
    schedule_time: str
    last_sent: Optional[datetime]
    is_active: bool
    recipient_imessage_id: str
    route_name: str

    class Config:
        from_attributes = True


@router.post("/process", response_model=iMessageResponse)
async def process_imessage(request: iMessageRequest):
    """Process an incoming iMessage and return response."""
    try:
        response_text = await imessage_service.process_incoming_message(
            request.sender, 
            request.message
        )
        
        return iMessageResponse(
            response=response_text or "No response generated",
            processed=True,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing iMessage: {str(e)}")


@router.post("/send")
async def send_imessage(
    recipient: str = Query(..., description="Recipient phone number or iMessage ID"),
    message: str = Query(..., description="Message to send")
):
    """Send an iMessage to a recipient."""
    try:
        success = await imessage_service.send_message(recipient, message)
        
        if success:
            return {
                "message": "iMessage sent successfully",
                "recipient": recipient,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send iMessage")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending iMessage: {str(e)}")


@router.post("/schedule", response_model=ScheduledMessageResponse)
async def create_scheduled_message(
    message_data: ScheduledMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new scheduled iMessage."""
    try:
        # Verify route exists and belongs to user
        route = db.query(Route).filter(
            Route.id == message_data.route_id,
            Route.user_id == current_user.id
        ).first()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Create scheduled message
        scheduled_message = ScheduledMessage(
            route_id=message_data.route_id,
            user_id=current_user.id,
            schedule_time=message_data.schedule_time,
            recipient_imessage_id=message_data.recipient_imessage_id,
            is_active=message_data.is_active,
            last_sent=None
        )
        
        db.add(scheduled_message)
        db.commit()
        db.refresh(scheduled_message)
        
        return ScheduledMessageResponse(
            id=scheduled_message.id,
            route_id=scheduled_message.route_id,
            user_id=scheduled_message.user_id,
            schedule_time=scheduled_message.schedule_time,
            last_sent=scheduled_message.last_sent,
            is_active=scheduled_message.is_active,
            recipient_imessage_id=scheduled_message.recipient_imessage_id,
            route_name=route.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating scheduled message: {str(e)}")


@router.get("/schedule", response_model=List[ScheduledMessageResponse])
async def get_scheduled_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's scheduled messages."""
    try:
        scheduled_messages = db.query(ScheduledMessage).filter(
            ScheduledMessage.user_id == current_user.id
        ).all()
        
        result = []
        for sm in scheduled_messages:
            route = db.query(Route).filter(Route.id == sm.route_id).first()
            result.append(ScheduledMessageResponse(
                id=sm.id,
                route_id=sm.route_id,
                user_id=sm.user_id,
                schedule_time=sm.schedule_time,
                last_sent=sm.last_sent,
                is_active=sm.is_active,
                recipient_imessage_id=sm.recipient_imessage_id,
                route_name=route.name if route else "Unknown Route"
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduled messages: {str(e)}")


@router.put("/schedule/{message_id}")
async def update_scheduled_message(
    message_id: int,
    message_data: ScheduledMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a scheduled message."""
    try:
        scheduled_message = db.query(ScheduledMessage).filter(
            ScheduledMessage.id == message_id,
            ScheduledMessage.user_id == current_user.id
        ).first()
        
        if not scheduled_message:
            raise HTTPException(status_code=404, detail="Scheduled message not found")
        
        # Update fields
        scheduled_message.schedule_time = message_data.schedule_time
        scheduled_message.recipient_imessage_id = message_data.recipient_imessage_id
        scheduled_message.is_active = message_data.is_active
        
        db.commit()
        
        return {
            "message": "Scheduled message updated successfully",
            "id": message_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating scheduled message: {str(e)}")


@router.delete("/schedule/{message_id}")
async def delete_scheduled_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scheduled message."""
    try:
        scheduled_message = db.query(ScheduledMessage).filter(
            ScheduledMessage.id == message_id,
            ScheduledMessage.user_id == current_user.id
        ).first()
        
        if not scheduled_message:
            raise HTTPException(status_code=404, detail="Scheduled message not found")
        
        db.delete(scheduled_message)
        db.commit()
        
        return {
            "message": "Scheduled message deleted successfully",
            "id": message_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting scheduled message: {str(e)}")


@router.post("/schedule/{message_id}/send")
async def send_scheduled_message_now(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a scheduled message immediately."""
    try:
        scheduled_message = db.query(ScheduledMessage).filter(
            ScheduledMessage.id == message_id,
            ScheduledMessage.user_id == current_user.id
        ).first()
        
        if not scheduled_message:
            raise HTTPException(status_code=404, detail="Scheduled message not found")
        
        success = await imessage_service.send_scheduled_route_summary(scheduled_message)
        
        if success:
            return {
                "message": "Scheduled message sent successfully",
                "id": message_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send scheduled message")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending scheduled message: {str(e)}")


@router.post("/process-scheduled")
async def process_scheduled_messages():
    """Process all due scheduled messages (internal endpoint)."""
    try:
        await imessage_service.process_scheduled_messages()
        
        return {
            "message": "Scheduled messages processed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing scheduled messages: {str(e)}")


@router.get("/test")
async def test_imessage_formatting():
    """Test iMessage formatting with sample data."""
    try:
        # Create sample weather data
        sample_weather = {
            'flight_category': 'VFR',
            'temp_c': 15.0,
            'dewpoint_c': 10.0,
            'wind_dir_degrees': 270,
            'wind_speed_kt': 8,
            'visibility_mi': 10.0,
            'altimeter_in_hg': 29.95,
            'sky_cover': 'CLR',
            'raw_text': 'KSFO 091800Z 27008KT 10SM CLR 15/10 A2995'
        }
        
        sample_airport = {
            'icao': 'KSFO',
            'name': 'San Francisco International Airport'
        }
        
        # Format the line
        formatted_line = imessage_service._format_weather_line(sample_airport, sample_weather)
        
        return {
            "sample_format": formatted_line,
            "description": "Sample weather line format",
            "example": "KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing formatting: {str(e)}")


@router.get("/commands")
async def get_imessage_commands():
    """Get available iMessage commands."""
    return {
        "commands": {
            "airport_codes": "Send airport codes (e.g., KSFO KLAX KJFK)",
            "route": "Get weather for a named route (e.g., ROUTE MyCommute)",
            "routes": "List your available routes",
            "status": "Check AirPuff service status",
            "help": "Show help message"
        },
        "examples": [
            "KSFO KLAX KJFK",
            "ROUTE MyCommute", 
            "ROUTE (uses favorite route)",
            "STATUS",
            "HELP"
        ],
        "limits": {
            "max_airports": 10,
            "max_message_length": 1600
        }
    }
