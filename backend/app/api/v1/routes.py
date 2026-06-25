"""Route API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.airport import Airport
from ...models.route import Route, RouteAirport
from ...models.user import User
from .auth import get_current_user, get_optional_current_user, is_admin

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
    airports: List[dict]

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


def _serialize_route(route: Route, db: Session) -> dict:
    """Serialize a route and its ordered airports."""

    route_dict = {
        "id": route.id,
        "name": route.name,
        "description": route.description,
        "user_id": route.user_id,
        "is_public": route.is_public,
        "is_favorite": route.is_favorite,
        "created_at": route.created_at,
        "updated_at": route.updated_at,
        "airports": [],
    }

    route_airports = (
        db.query(RouteAirport)
        .filter(RouteAirport.route_id == route.id)
        .order_by(RouteAirport.order)
        .all()
    )

    for route_airport in route_airports:
        airport = db.query(Airport).filter(Airport.id == route_airport.airport_id).first()
        if airport:
            route_dict["airports"].append(
                {
                    "icao": airport.icao,
                    "name": airport.name,
                    "order": route_airport.order,
                    "notes": route_airport.notes,
                    "is_waypoint": route_airport.is_waypoint,
                }
            )

    return route_dict


def _can_view_route(route: Route, current_user: Optional[User]) -> bool:
    """Return whether the current user can view the route."""

    if route.is_public:
        return True
    if current_user is None:
        return False
    if route.user_id == current_user.id:
        return True
    return is_admin(current_user)


@router.get("/", response_model=List[RouteResponse])
async def list_routes(
    user_id: Optional[int] = Query(None),
    public_only: bool = Query(False),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """List routes for the current user or public routes."""

    query = db.query(Route)

    if public_only:
        query = query.filter(Route.is_public.is_(True))
    elif user_id is not None:
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if user_id != current_user.id and not is_admin(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to view these routes")
        query = query.filter(Route.user_id == user_id)
    else:
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if not is_admin(current_user):
            query = query.filter(Route.user_id == current_user.id)

    routes = query.order_by(Route.updated_at.desc()).all()
    visible_routes = [
        _serialize_route(route, db)
        for route in routes
        if _can_view_route(route, current_user)
    ]
    return visible_routes


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific route by ID."""

    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if not _can_view_route(route, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view this route")
    return _serialize_route(route, db)


@router.post("/", response_model=RouteResponse)
async def create_route(
    route: RouteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new route."""

    db_route = Route(
        name=route.name,
        description=route.description,
        user_id=current_user.id,
        is_public=route.is_public,
        is_favorite=route.is_favorite,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    for order, icao in enumerate(route.airport_icaos):
        airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
        if airport:
            db.add(
                RouteAirport(
                    route_id=db_route.id,
                    airport_id=airport.id,
                    order=order,
                    is_waypoint=False,
                )
            )

    db.commit()
    db.refresh(db_route)
    return _serialize_route(db_route, db)


@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    route: RouteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing route."""

    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    if db_route.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to update this route")

    update_data = route.model_dump(exclude_unset=True)
    airport_icaos = update_data.pop("airport_icaos", None)

    for field, value in update_data.items():
        setattr(db_route, field, value)

    if airport_icaos is not None:
        db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
        for order, icao in enumerate(airport_icaos):
            airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
            if airport:
                db.add(
                    RouteAirport(
                        route_id=route_id,
                        airport_id=airport.id,
                        order=order,
                        is_waypoint=False,
                    )
                )

    db_route.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_route)
    return _serialize_route(db_route, db)


@router.delete("/{route_id}")
async def delete_route(
    route_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a route."""

    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if route.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this route")

    db.query(RouteAirport).filter(RouteAirport.route_id == route_id).delete()
    db.delete(route)
    db.commit()
    return {"message": "Route deleted successfully"}
