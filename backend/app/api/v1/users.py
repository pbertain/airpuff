"""User management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ...database import get_db
from ...models.user import User
from ...api.v1.auth import get_current_user

router = APIRouter()


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    units: Optional[str] = None
    default_airports: Optional[str] = None  # JSON string of ICAO codes


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    provider: str
    units: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics model."""
    total_routes: int
    public_routes: int
    favorite_routes: int
    total_airports: int
    account_age_days: int


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user statistics."""
    from ...models.route import Route
    
    # Count user's routes
    total_routes = db.query(Route).filter(Route.user_id == current_user.id).count()
    public_routes = db.query(Route).filter(
        Route.user_id == current_user.id,
        Route.is_public == True
    ).count()
    favorite_routes = db.query(Route).filter(
        Route.user_id == current_user.id,
        Route.is_favorite == True
    ).count()
    
    # Count unique airports in user's routes
    from ...models.route import RouteAirport
    total_airports = db.query(RouteAirport.airport_id).join(Route).filter(
        Route.user_id == current_user.id
    ).distinct().count()
    
    # Calculate account age
    account_age_days = (datetime.utcnow() - current_user.created_at).days
    
    return UserStats(
        total_routes=total_routes,
        public_routes=public_routes,
        favorite_routes=favorite_routes,
        total_airports=total_airports,
        account_age_days=account_age_days
    )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    # In a real application, you might want to:
    # 1. Soft delete (mark as inactive)
    # 2. Anonymize data instead of deleting
    # 3. Send confirmation email first
    
    # For now, we'll just mark as inactive
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}


@router.get("/public", response_model=List[UserResponse])
async def get_public_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of public users (for route sharing, etc.)."""
    users = db.query(User).filter(
        User.is_active == True,
        User.is_verified == True
    ).offset(skip).limit(limit).all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID (public information only)."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
