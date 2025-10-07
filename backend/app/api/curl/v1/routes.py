"""cURL-friendly route endpoints with clear-text output."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...database import get_db
from ...models.route import Route, RouteAirport, ScheduledMessage
from ...models.airport import Airport
from ...models.user import User

router = APIRouter()


class RouteCreate(BaseModel):
    """Route creation model for cURL."""
    name: str
    description: Optional[str] = None
    airport_icaos: List[str]
    is_public: bool = False
    is_favorite: bool = False


def format_route_text(route: Route, airports: List[Airport]) -> str:
    """Format route data as clear text."""
    lines = [
        f"Route: {route.name}",
        f"Description: {route.description or 'N/A'}",
        f"User ID: {route.user_id}",
        f"Public: {'Yes' if route.is_public else 'No'}",
        f"Favorite: {'Yes' if route.is_favorite else 'No'}",
        f"Created: {route.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Updated: {route.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "Airports:"
    ]
    
    # Get route airports in order
    route_airports = sorted(route.airports, key=lambda ra: ra.order if hasattr(ra, 'order') else 0)
    
    for i, airport in enumerate(route_airports, 1):
        lines.append(f"  {i}. {airport.icao} - {airport.name or 'Unknown'}")
        if airport.city:
            lines.append(f"     {airport.city}, {airport.state or ''} {airport.country or ''}")
    
    lines.append("---")
    return "\n".join(lines)


@router.get("/", response_class=Response)
async def list_routes_curl(
    user_id: Optional[int] = Query(None),
    public_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List routes in clear text format."""
    query = db.query(Route)
    
    if user_id:
        query = query.filter(Route.user_id == user_id)
    elif public_only:
        query = query.filter(Route.is_public == True)
    
    routes = query.all()
    
    if not routes:
        return Response(content="No routes found.\n", media_type="text/plain")
    
    output_lines = [f"Found {len(routes)} routes:\n"]
    
    for i, route in enumerate(routes, 1):
        output_lines.append(f"{i}. {route.name} (ID: {route.id})")
        output_lines.append(f"   User: {route.user_id} | Public: {'Yes' if route.is_public else 'No'} | Favorite: {'Yes' if route.is_favorite else 'No'}")
        output_lines.append(f"   Created: {route.created_at.strftime('%Y-%m-%d %H:%M')}")
        if route.description:
            output_lines.append(f"   Description: {route.description}")
        output_lines.append("")
    
    return Response(content="\n".join(output_lines), media_type="text/plain")


@router.get("/{route_id}", response_class=Response)
async def get_route_curl(route_id: int, db: Session = Depends(get_db)):
    """Get a specific route by ID in clear text format."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        return Response(content=f"Route {route_id} not found.\n", media_type="text/plain", status_code=404)
    
    # Get airports for this route
    route_airports = db.query(RouteAirport).filter(
        RouteAirport.route_id == route.id
    ).order_by(RouteAirport.order).all()
    
    airports = []
    for ra in route_airports:
        airport = db.query(Airport).filter(Airport.id == ra.airport_id).first()
        if airport:
            airports.append(airport)
    
    return Response(content=format_route_text(route, airports), media_type="text/plain")


@router.post("/", response_class=Response)
async def create_route_curl(route: RouteCreate, db: Session = Depends(get_db)):
    """Create a new route and return confirmation."""
    # TODO: Add user authentication to get user_id
    user_id = 1  # Placeholder - will be replaced with actual user from auth
    
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
    airports = []
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
            airports.append(airport)
    
    db.commit()
    
    output = f"Route '{route.name}' created successfully (ID: {db_route.id}).\n\n{format_route_text(db_route, airports)}"
    return Response(content=output, media_type="text/plain", status_code=201)


@router.put("/{route_id}", response_class=Response)
async def update_route_curl(
    route_id: int,
    route: RouteCreate,
    db: Session = Depends(get_db)
):
    """Update an existing route and return confirmation."""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        return Response(content=f"Route {route_id} not found.\n", media_type="text/plain", status_code=404)
    
    # Update route fields
    db_route.name = route.name
    db_route.description = route.description
    db_route.is_public = route.is_public
    db_route.is_favorite = route.is_favorite
    db_route.updated_at = datetime.utcnow()
    
    # Handle airport updates
    if route.airport_icaos is not None:
        # Remove existing airports
        db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
        
        # Add new airports
        airports = []
        for i, icao in enumerate(route.airport_icaos):
            airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
            if airport:
                route_airport = RouteAirport(
                    route_id=route_id,
                    airport_id=airport.id,
                    order=i,
                    is_waypoint=False
                )
                db.add(route_airport)
                airports.append(airport)
    else:
        # Get existing airports
        route_airports = db.query(RouteAirport).filter(RouteAirport.route_id == route_id).all()
        airports = [db.query(Airport).filter(Airport.id == ra.airport_id).first() for ra in route_airports]
        airports = [a for a in airports if a is not None]
    
    db.commit()
    
    output = f"Route '{route.name}' updated successfully.\n\n{format_route_text(db_route, airports)}"
    return Response(content=output, media_type="text/plain")


@router.delete("/{route_id}", response_class=Response)
async def delete_route_curl(route_id: int, db: Session = Depends(get_db)):
    """Delete a route and return confirmation."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        return Response(content=f"Route {route_id} not found.\n", media_type="text/plain", status_code=404)
    
    # Delete associated route airports
    db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
    
    # Delete route
    db.delete(route)
    db.commit()
    
    return Response(content=f"Route '{route.name}' (ID: {route_id}) deleted successfully.\n", media_type="text/plain")
