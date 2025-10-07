"""Authentication API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from ...database import get_db
from ...models.user import User
from ...config import settings

router = APIRouter()
security = HTTPBearer()


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    provider: str
    units: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    google_token: str,
    db: Session = Depends(get_db)
):
    """Authenticate with Google OAuth token."""
    # TODO: Implement Google OAuth token validation
    # This is a placeholder - in production, you would:
    # 1. Validate the Google token with Google's API
    # 2. Extract user information from the token
    # 3. Create or update user in database
    # 4. Return JWT token
    
    # Placeholder user creation/update
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            name="Test User",
            provider="google",
            provider_id="123456789",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/apple", response_model=TokenResponse)
async def apple_auth(
    apple_token: str,
    db: Session = Depends(get_db)
):
    """Authenticate with Apple OAuth token."""
    # TODO: Implement Apple OAuth token validation
    # Similar to Google auth but with Apple's validation process
    
    # Placeholder implementation
    user = db.query(User).filter(User.email == "test@apple.com").first()
    if not user:
        user = User(
            email="test@apple.com",
            name="Apple User",
            provider="apple",
            provider_id="987654321",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }
