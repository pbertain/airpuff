"""Route API endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import get_db
from ...models.route import Route, RouteAirport, ScheduledMessage
from ...models.airport import Airport
from ...models.user import User
from .auth import get_current_user

router = APIRouter()


class RouteResponse(BaseModel):
    """Route response model."""
    id: int
    name: str
    description: Optional[str]
    user_id: int
    is_public: bool
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    airports: List[dict]  # Will be populated with airport details

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    """Route creation model."""
    name: str
    description: Optional[str] = None
    airport_icaos: List[str]
    is_public: bool = False
    is_favorite: bool = False


class RouteUpdate(BaseModel):
    """Route update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    airport_icaos: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None


@router.get("/", response_model=List[RouteResponse])
async def list_routes(
    user_id: Optional[int] = Query(None),
    public_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List routes, optionally filtered by user or public routes."""
    query = db.query(Route)
    
    if user_id:
        query = query.filter(Route.user_id == user_id)
    elif public_only:
        query = query.filter(Route.is_public == True)
    
    routes = query.all()
    
    # Populate airport details for each route
    result = []
    for route in routes:
        route_dict = {
            "id": route.id,
            "name": route.name,
            "description": route.description,
            "user_id": route.user_id,
            "is_public": route.is_public,
            "is_favorite": route.is_favorite,
            "created_at": route.created_at,
            "updated_at": route.updated_at,
            "airports": []
        }
        
        # Get airports for this route
        route_airports = db.query(RouteAirport).filter(
            RouteAirport.route_id == route.id
        ).order_by(RouteAirport.order).all()
        
        for ra in route_airports:
            airport = db.query(Airport).filter(Airport.id == ra.airport_id).first()
            if airport:
                route_dict["airports"].append({
                    "icao": airport.icao,
                    "name": airport.name,
                    "order": ra.order,
                    "notes": ra.notes,
                    "is_waypoint": ra.is_waypoint
                })
        
        result.append(route_dict)
    
    return result


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get a specific route by ID."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Populate airport details
    route_dict = {
        "id": route.id,
        "name": route.name,
        "description": route.description,
        "user_id": route.user_id,
        "is_public": route.is_public,
        "is_favorite": route.is_favorite,
        "created_at": route.created_at,
        "updated_at": route.updated_at,
        "airports": []
    }
    
    # Get airports for this route
    route_airports = db.query(RouteAirport).filter(
        RouteAirport.route_id == route.id
    ).order_by(RouteAirport.order).all()
    
    for ra in route_airports:
        airport = db.query(Airport).filter(Airport.id == ra.airport_id).first()
        if airport:
            route_dict["airports"].append({
                "icao": airport.icao,
                "name": airport.name,
                "order": ra.order,
                "notes": ra.notes,
                "is_waypoint": ra.is_waypoint
            })
    
    return route_dict


@router.post("/", response_model=RouteResponse)
async def create_route(
    route: RouteCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new route."""
    user_id = current_user.id
    
    # Create route
    db_route = Route(
        name=route.name,
        description=route.description,
        user_id=user_id,
        is_public=route.is_public,
        is_favorite=route.is_favorite,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    
    # Add airports to route
    for i, icao in enumerate(route.airport_icaos):
        airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
        if airport:
            route_airport = RouteAirport(
                route_id=db_route.id,
                airport_id=airport.id,
                order=i,
                is_waypoint=False
            )
            db.add(route_airport)
    
    db.commit()
    
    return get_route(db_route.id, db)


@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    route: RouteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing route."""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Check if user owns the route
    if db_route.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this route")
    
    # Update route fields
    for field, value in route.dict(exclude_unset=True).items():
        if field == "airport_icaos":
            # Handle airport updates
            if value is not None:
                # Remove existing airports
                db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
                
                # Add new airports
                for i, icao in enumerate(value):
                    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
                    if airport:
                        route_airport = RouteAirport(
                            route_id=route_id,
                            airport_id=airport.id,
                            order=i,
                            is_waypoint=False
                        )
                        db.add(route_airport)
        else:
            setattr(db_route, field, value)
    
    db_route.updated_at = datetime.utcnow()
    db.commit()
    
    return get_route(route_id, db)


@router.delete("/{route_id}")
async def delete_route(
    route_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a route."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Check if user owns the route
    if route.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this route")
    
    # Delete associated route airports
    db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
    
    # Delete route
    db.delete(route)
    db.commit()
    
    return {"message": "Route deleted successfully"}
