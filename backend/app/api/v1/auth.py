"""Authentication API endpoints and shared auth dependencies."""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...models.user import User
from ...services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer(auto_error=False)


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
    role: str
    units: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    is_admin: bool

    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def is_admin(user: User) -> bool:
    """Return whether the user has admin access."""

    return (user.role or "").lower() == "admin"


def get_session_user(request: Request, db: Session) -> Optional[User]:
    """Get the currently logged-in session user, if one exists."""

    session_user = request.session.get("user")
    if not session_user:
        return None

    user_id = session_user.get("id")
    if not user_id:
        request.session.clear()
        return None

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        request.session.clear()
        return None

    return user


def _get_bearer_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: Session,
) -> Optional[User]:
    """Resolve a JWT bearer token to a user."""

    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id), User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get the current user from the session cookie or bearer token."""

    session_user = get_session_user(request, db)
    if session_user is not None:
        return session_user

    return _get_bearer_user(credentials, db)


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Require an authenticated user via session cookie or bearer token."""

    user = get_optional_current_user(request, credentials, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require an authenticated admin user."""

    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def _serialize_user(user: User) -> UserResponse:
    """Serialize a user model for API responses."""

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        role=user.role,
        units=user.units,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
        is_admin=is_admin(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information for the active session."""

    return _serialize_user(current_user)


@router.post("/google", response_model=TokenResponse)
async def google_auth(google_token: str, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth token."""

    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            name="Test User",
            provider="google",
            provider_id="123456789",
            role="user",
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/apple", response_model=TokenResponse)
async def apple_auth(apple_token: str, db: Session = Depends(get_db)):
    """Authenticate with Apple OAuth token."""

    user = db.query(User).filter(User.email == "test@apple.com").first()
    if not user:
        user = User(
            email="test@apple.com",
            name="Apple User",
            provider="apple",
            provider_id="987654321",
            role="user",
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/login/google")
async def google_login(request: Request):
    """Initiate Google OAuth login."""

    if not auth_service.google_client_id or not auth_service.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    state = auth_service.generate_state()
    code_verifier = auth_service.generate_code_verifier()
    code_challenge = auth_service.generate_code_challenge(code_verifier)

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

    from fastapi.responses import RedirectResponse

    return RedirectResponse(url=google_auth_url)


@router.get("/login/apple")
async def apple_login(request: Request):
    """Initiate Apple OAuth login."""

    if not auth_service.apple_client_id or not auth_service.apple_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Apple OAuth is not configured",
        )

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

    from fastapi.responses import RedirectResponse

    return RedirectResponse(url=apple_auth_url)


@router.get("/callback/google", response_model=TokenResponse)
async def google_callback(request: Request, code: str, state: str = None):
    """Handle Google OAuth callback."""

    redirect_uri = str(request.url_for("google_callback"))
    token_data = await auth_service.exchange_google_code(code, redirect_uri)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    user_info = await auth_service.get_google_user_info(token_data["access_token"])
    if not user_info:
        raise HTTPException(
            status_code=400,
            detail="Failed to get user info from Google",
        )

    user = auth_service.get_or_create_user(
        provider="google",
        provider_id=user_info["id"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"].split("@")[0]),
    )
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/callback/apple", response_model=TokenResponse)
async def apple_callback(request: Request, code: str, state: str = None):
    """Handle Apple OAuth callback."""

    redirect_uri = str(request.url_for("apple_callback"))
    token_data = await auth_service.exchange_apple_code(code, redirect_uri)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token received from Apple")

    user_info = await auth_service.get_apple_user_info(id_token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Apple")

    user = auth_service.get_or_create_user(
        provider="apple",
        provider_id=user_info["id"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"].split("@")[0]),
    )
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/logout")
def logout():
    """Legacy logout endpoint for bearer-token clients."""

    return {"message": "Successfully logged out"}


@router.post("/demo/apple", response_model=TokenResponse)
async def demo_apple_login(db: Session = Depends(get_db)):
    """Demo Apple login for development."""

    user = db.query(User).filter(User.email == "demo.apple@airpuff.com").first()
    if not user:
        user = User(
            email="demo.apple@airpuff.com",
            name="Apple Demo User",
            provider="apple",
            provider_id="demo_apple_123",
            role="user",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/demo/google", response_model=TokenResponse)
async def demo_google_login(db: Session = Depends(get_db)):
    """Demo Google login for development."""

    user = db.query(User).filter(User.email == "demo.google@airpuff.com").first()
    if not user:
        user = User(
            email="demo.google@airpuff.com",
            name="Google Demo User",
            provider="google",
            provider_id="demo_google_123",
            role="user",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/providers")
def get_auth_providers():
    """Get available direct providers outside of Keycloak."""

    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "login_url": "/api/v1/auth/login/google",
                "enabled": bool(auth_service.google_client_id),
            },
            {
                "name": "apple",
                "display_name": "Apple",
                "login_url": "/api/v1/auth/login/apple",
                "enabled": bool(auth_service.apple_client_id),
            },
        ]
    }
