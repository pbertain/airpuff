"""Admin-only endpoints for application setup and configuration."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.admin import RouteTemplate, RouteTemplateAirport
from ...models.airport import Airport
from ...models.user import User
from .auth import require_admin

router = APIRouter()


class AdminAirportResponse(BaseModel):
    """Airport payload for the admin UI."""

    id: int
    icao: str
    name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    elevation_ft: Optional[int]
    atis_phone: Optional[str]
    tower_phone: Optional[str]
    is_monitored: bool

    class Config:
        from_attributes = True


class AdminAirportCreate(BaseModel):
    """Airport create/update payload for admins."""

    icao: str
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_ft: Optional[int] = None
    atis_phone: Optional[str] = None
    tower_phone: Optional[str] = None
    is_monitored: bool = True


class RouteTemplateResponse(BaseModel):
    """Admin-managed route template response."""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    airports: List[dict]


class RouteTemplateCreate(BaseModel):
    """Create payload for a route template."""

    name: str
    description: Optional[str] = None
    airport_icaos: List[str]
    is_active: bool = True


class RouteTemplateUpdate(BaseModel):
    """Update payload for a route template."""

    name: Optional[str] = None
    description: Optional[str] = None
    airport_icaos: Optional[List[str]] = None
    is_active: Optional[bool] = None


def _serialize_route_template(route_template: RouteTemplate) -> dict:
    """Serialize a route template including airport order."""

    return {
        "id": route_template.id,
        "name": route_template.name,
        "description": route_template.description,
        "is_active": route_template.is_active,
        "created_at": route_template.created_at,
        "updated_at": route_template.updated_at,
        "airports": [
            {
                "icao": detail.airport.icao,
                "name": detail.airport.name,
                "order": detail.order,
            }
            for detail in route_template.airports
            if detail.airport is not None
        ],
    }


@router.get("/summary")
async def admin_summary(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return lightweight admin dashboard metrics."""

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
        },
        "counts": {
            "monitored_airports": db.query(Airport).filter(Airport.is_monitored.is_(True)).count(),
            "all_airports": db.query(Airport).count(),
            "route_templates": db.query(RouteTemplate).count(),
        },
    }


@router.get("/airports", response_model=List[AdminAirportResponse])
async def list_admin_airports(
    search: Optional[str] = Query(None),
    monitored_only: bool = Query(False),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List airports for admin management."""

    query = db.query(Airport)
    if monitored_only:
        query = query.filter(Airport.is_monitored.is_(True))
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Airport.icao.ilike(pattern)
            | Airport.name.ilike(pattern)
            | Airport.city.ilike(pattern)
        )
    return query.order_by(Airport.icao.asc()).limit(250).all()


@router.post("/airports", response_model=AdminAirportResponse)
async def create_or_update_admin_airport(
    payload: AdminAirportCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create an airport or update it if the ICAO already exists."""

    airport = db.query(Airport).filter(Airport.icao == payload.icao.upper()).first()
    if airport is None:
        airport = Airport(icao=payload.icao.upper())
        db.add(airport)

    for field, value in payload.model_dump().items():
        if field == "icao":
            airport.icao = value.upper()
        else:
            setattr(airport, field, value)

    db.commit()
    db.refresh(airport)
    return airport


@router.delete("/airports/{icao}")
async def delete_admin_airport(
    icao: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete an airport from the system."""

    airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")

    db.delete(airport)
    db.commit()
    return {"message": f"Deleted airport {icao.upper()}"}


@router.get("/route-templates", response_model=List[RouteTemplateResponse])
async def list_route_templates(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all admin-managed route templates."""

    templates = db.query(RouteTemplate).order_by(RouteTemplate.updated_at.desc()).all()
    return [_serialize_route_template(route_template) for route_template in templates]


@router.post("/route-templates", response_model=RouteTemplateResponse)
async def create_route_template(
    payload: RouteTemplateCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new route template."""

    now = datetime.utcnow()
    route_template = RouteTemplate(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
        created_at=now,
        updated_at=now,
    )
    db.add(route_template)
    db.flush()
    _replace_route_template_airports(db, route_template, payload.airport_icaos)
    db.commit()
    db.refresh(route_template)
    return _serialize_route_template(route_template)


@router.put("/route-templates/{template_id}", response_model=RouteTemplateResponse)
async def update_route_template(
    template_id: int,
    payload: RouteTemplateUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update an existing route template."""

    route_template = db.query(RouteTemplate).filter(RouteTemplate.id == template_id).first()
    if route_template is None:
        raise HTTPException(status_code=404, detail="Route template not found")

    update_data = payload.model_dump(exclude_unset=True)
    airport_icaos = update_data.pop("airport_icaos", None)
    for field, value in update_data.items():
        setattr(route_template, field, value)

    if airport_icaos is not None:
        _replace_route_template_airports(db, route_template, airport_icaos)

    route_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(route_template)
    return _serialize_route_template(route_template)


@router.delete("/route-templates/{template_id}")
async def delete_route_template(
    template_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a route template."""

    route_template = db.query(RouteTemplate).filter(RouteTemplate.id == template_id).first()
    if route_template is None:
        raise HTTPException(status_code=404, detail="Route template not found")

    db.delete(route_template)
    db.commit()
    return {"message": f"Deleted route template {template_id}"}


def _replace_route_template_airports(
    db: Session,
    route_template: RouteTemplate,
    airport_icaos: List[str],
) -> None:
    """Replace the ordered airport list for a route template."""

    db.query(RouteTemplateAirport).filter(
        RouteTemplateAirport.route_template_id == route_template.id
    ).delete()

    for order, icao in enumerate(airport_icaos):
        airport = db.query(Airport).filter(Airport.icao == icao.upper()).first()
        if airport is None:
            raise HTTPException(
                status_code=400,
                detail=f"Airport {icao.upper()} must exist before adding it to a route template",
            )
        db.add(
            RouteTemplateAirport(
                route_template_id=route_template.id,
                airport_id=airport.id,
                order=order,
            )
        )

    route_template.updated_at = datetime.utcnow()
    db.flush()
