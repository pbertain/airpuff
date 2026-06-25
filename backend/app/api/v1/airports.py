"""Airport API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import get_db
from ...models.airport import Airport
from .auth import require_admin

router = APIRouter()


class AirportResponse(BaseModel):
    """Airport response model."""
    id: int
    icao: str
    name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    elevation_ft: Optional[int]
    atis_phone: Optional[str]
    tower_phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    is_monitored: bool

    class Config:
        from_attributes = True


class AirportCreate(BaseModel):
    """Airport creation model."""
    icao: str
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_ft: Optional[int] = None
    atis_phone: Optional[str] = None
    tower_phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_monitored: bool = False


@router.get("/", response_model=List[AirportResponse])
async def list_airports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all airports with optional search."""
    query = db.query(Airport)
    
    if search:
        query = query.filter(
            Airport.icao.ilike(f"%{search}%") |
            Airport.name.ilike(f"%{search}%") |
            Airport.city.ilike(f"%{search}%")
        )
    
    airports = query.offset(skip).limit(limit).all()
    return airports


@router.get("/{icao}", response_model=AirportResponse)
async def get_airport(icao: str, db: Session = Depends(get_db)):
    """Get airport by ICAO code."""
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport


@router.post("/", response_model=AirportResponse)
async def create_airport(
    airport: AirportCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    """Create a new airport."""
    # Check if airport already exists
    existing = db.query(Airport).filter(Airport.icao == airport.icao.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Airport already exists")
    
    # Create new airport
    db_airport = Airport(
        icao=airport.icao.upper(),
        name=airport.name,
        latitude=airport.latitude,
        longitude=airport.longitude,
        elevation_ft=airport.elevation_ft,
        atis_phone=airport.atis_phone,
        tower_phone=airport.tower_phone,
        city=airport.city,
        state=airport.state,
        country=airport.country,
        is_monitored=airport.is_monitored,
    )
    
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    
    return db_airport


@router.put("/{icao}", response_model=AirportResponse)
async def update_airport(
    icao: str, 
    airport: AirportCreate, 
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    """Update an existing airport."""
    db_airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not db_airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Update fields
    for field, value in airport.model_dump(exclude_unset=True).items():
        setattr(db_airport, field, value)
    
    db.commit()
    db.refresh(db_airport)
    
    return db_airport


@router.delete("/{icao}")
async def delete_airport(
    icao: str,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    """Delete an airport."""
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    db.delete(airport)
    db.commit()
    
    return {"message": "Airport deleted successfully"}
