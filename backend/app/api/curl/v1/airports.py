"""cURL-friendly airport endpoints with clear-text output."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import get_db
from ...models.airport import Airport

router = APIRouter()


class AirportCreate(BaseModel):
    """Airport creation model for cURL."""
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


def format_airport_text(airport: Airport) -> str:
    """Format airport data as clear text."""
    lines = [
        f"ICAO: {airport.icao}",
        f"Name: {airport.name or 'N/A'}",
        f"Location: {airport.city or 'N/A'}, {airport.state or 'N/A'}, {airport.country or 'N/A'}",
        f"Coordinates: {airport.latitude or 'N/A'}, {airport.longitude or 'N/A'}",
        f"Elevation: {airport.elevation_ft or 'N/A'} ft",
        f"ATIS Phone: {airport.atis_phone or 'N/A'}",
        f"Tower Phone: {airport.tower_phone or 'N/A'}",
        "---"
    ]
    return "\n".join(lines)


@router.get("/", response_class=Response)
async def list_airports_curl(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all airports in clear text format."""
    query = db.query(Airport)
    
    if search:
        query = query.filter(
            Airport.icao.ilike(f"%{search}%") |
            Airport.name.ilike(f"%{search}%") |
            Airport.city.ilike(f"%{search}%")
        )
    
    airports = query.offset(skip).limit(limit).all()
    
    if not airports:
        return Response(content="No airports found.\n", media_type="text/plain")
    
    output_lines = [f"Found {len(airports)} airports:\n"]
    
    for i, airport in enumerate(airports, 1):
        output_lines.append(f"{i}. {airport.icao} - {airport.name or 'Unknown'}")
        if airport.city:
            output_lines.append(f"   {airport.city}, {airport.state or ''} {airport.country or ''}")
        output_lines.append("")
    
    return Response(content="\n".join(output_lines), media_type="text/plain")


@router.get("/{icao}", response_class=Response)
async def get_airport_curl(icao: str, db: Session = Depends(get_db)):
    """Get airport details in clear text format."""
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        return Response(content=f"Airport {icao.upper()} not found.\n", media_type="text/plain", status_code=404)
    
    return Response(content=format_airport_text(airport), media_type="text/plain")


@router.post("/", response_class=Response)
async def create_airport_curl(airport: AirportCreate, db: Session = Depends(get_db)):
    """Create a new airport and return confirmation."""
    # Check if airport already exists
    existing = db.query(Airport).filter(Airport.icao == airport.icao.upper()).first()
    if existing:
        return Response(
            content=f"Airport {airport.icao.upper()} already exists.\n",
            media_type="text/plain",
            status_code=400
        )
    
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
        country=airport.country
    )
    
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    
    output = f"Airport {airport.icao.upper()} created successfully.\n\n{format_airport_text(db_airport)}"
    return Response(content=output, media_type="text/plain", status_code=201)


@router.put("/{icao}", response_class=Response)
async def update_airport_curl(
    icao: str, 
    airport: AirportCreate, 
    db: Session = Depends(get_db)
):
    """Update an existing airport and return confirmation."""
    db_airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not db_airport:
        return Response(
            content=f"Airport {icao.upper()} not found.\n",
            media_type="text/plain",
            status_code=404
        )
    
    # Update fields
    for field, value in airport.dict(exclude_unset=True).items():
        setattr(db_airport, field, value)
    
    db.commit()
    db.refresh(db_airport)
    
    output = f"Airport {icao.upper()} updated successfully.\n\n{format_airport_text(db_airport)}"
    return Response(content=output, media_type="text/plain")


@router.delete("/{icao}", response_class=Response)
async def delete_airport_curl(icao: str, db: Session = Depends(get_db)):
    """Delete an airport and return confirmation."""
    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if not airport:
        return Response(
            content=f"Airport {icao.upper()} not found.\n",
            media_type="text/plain",
            status_code=404
        )
    
    db.delete(airport)
    db.commit()
    
    return Response(content=f"Airport {icao.upper()} deleted successfully.\n", media_type="text/plain")
