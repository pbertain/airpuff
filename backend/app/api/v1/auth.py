"""Authentication API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import httpx

from ...database import get_db
from ...models.user import User
from ...config import settings
from ...services.auth_service import auth_service

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


# OAuth 2.0 Flow Endpoints
@router.get("/login/google")
async def google_login(request: Request):
    """Initiate Google OAuth login."""
    # Check if Google OAuth is properly configured
    if not auth_service.google_client_id or not auth_service.google_client_secret:
        # Return a demo login page for development
        return RedirectResponse(url="/login?demo=google")
    
    state = auth_service.generate_state()
    code_verifier = auth_service.generate_code_verifier()
    code_challenge = auth_service.generate_code_challenge(code_verifier)
    
    # Store state and code_verifier in session (in production, use Redis or database)
    # For now, we'll pass them as query parameters
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={auth_service.google_client_id}&"
        f"redirect_uri={request.url_for('google_callback')}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    return RedirectResponse(url=google_auth_url)


@router.get("/login/apple")
async def apple_login(request: Request):
    """Initiate Apple OAuth login."""
    # Check if Apple OAuth is properly configured
    if not auth_service.apple_client_id or not auth_service.apple_client_secret:
        # Return a demo login page for development
        return RedirectResponse(url="/login?demo=apple")
    
    state = auth_service.generate_state()
    code_verifier = auth_service.generate_code_verifier()
    code_challenge = auth_service.generate_code_challenge(code_verifier)
    
    apple_auth_url = (
        f"https://appleid.apple.com/auth/authorize?"
        f"client_id={auth_service.apple_client_id}&"
        f"redirect_uri={request.url_for('apple_callback')}&"
        f"scope=name email&"
        f"response_type=code&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    return RedirectResponse(url=apple_auth_url)


@router.get("/callback/google", response_model=TokenResponse)
async def google_callback(request: Request, code: str, state: str = None):
    """Handle Google OAuth callback."""
    redirect_uri = str(request.url_for('google_callback'))
    
    # Exchange code for access token
    token_data = await auth_service.exchange_google_code(code, redirect_uri)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    # Get user info from Google
    user_info = await auth_service.get_google_user_info(token_data["access_token"])
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    # Get or create user
    user = auth_service.get_or_create_user(
        provider="google",
        provider_id=user_info["id"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"].split('@')[0])
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.get("/callback/apple", response_model=TokenResponse)
async def apple_callback(request: Request, code: str, state: str = None):
    """Handle Apple OAuth callback."""
    redirect_uri = str(request.url_for('apple_callback'))
    
    # Exchange code for access token
    token_data = await auth_service.exchange_apple_code(code, redirect_uri)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    # Apple returns an ID token in the response, not an access token
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token received from Apple")
    
    # Get user info from Apple ID token
    user_info = await auth_service.get_apple_user_info(id_token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Apple")
    
    # Get or create user
    user = auth_service.get_or_create_user(
        provider="apple",
        provider_id=user_info["id"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"].split('@')[0])
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/logout")
def logout():
    """Logout user (client should discard token)."""
    return {"message": "Successfully logged out"}


@router.post("/demo/apple", response_model=TokenResponse)
async def demo_apple_login(db: Session = Depends(get_db)):
    """Demo Apple login for development."""
    # Create a demo Apple user
    user = db.query(User).filter(User.email == "demo.apple@airpuff.com").first()
    if not user:
        user = User(
            email="demo.apple@airpuff.com",
            name="Apple Demo User",
            provider="apple",
            provider_id="demo_apple_123",
            is_active=True,
            is_verified=True,
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


@router.post("/demo/google", response_model=TokenResponse)
async def demo_google_login(db: Session = Depends(get_db)):
    """Demo Google login for development."""
    # Create a demo Google user
    user = db.query(User).filter(User.email == "demo.google@airpuff.com").first()
    if not user:
        user = User(
            email="demo.google@airpuff.com",
            name="Google Demo User",
            provider="google",
            provider_id="demo_google_123",
            is_active=True,
            is_verified=True,
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


@router.get("/providers")
def get_auth_providers():
    """Get available authentication providers."""
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "login_url": "/api/v1/auth/login/google",
                "enabled": bool(auth_service.google_client_id)
            },
            {
                "name": "apple",
                "display_name": "Apple",
                "login_url": "/api/v1/auth/login/apple",
                "enabled": bool(auth_service.apple_client_id)
            }
        ]
    }
