"""Authentication service for OAuth 2.0 providers."""

import httpx
import secrets
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..config import settings
from ..models.user import User
from ..database import SessionLocal


class AuthService:
    """Service for handling OAuth 2.0 authentication."""
    
    def __init__(self):
        self.google_client_id = settings.google_client_id
        self.google_client_secret = settings.google_client_secret
        self.apple_client_id = settings.apple_client_id
        self.apple_client_secret = settings.apple_client_secret
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def generate_state(self) -> str:
        """Generate a random state parameter for OAuth."""
        return secrets.token_urlsafe(32)
    
    def generate_code_verifier(self) -> str:
        """Generate a code verifier for PKCE."""
        return secrets.token_urlsafe(32)
    
    def generate_code_challenge(self, code_verifier: str) -> str:
        """Generate a code challenge from code verifier for PKCE."""
        digest = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip('=')
    
    async def get_google_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    async def get_apple_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Apple using access token."""
        try:
            # Apple returns user info in the ID token, not via a separate endpoint
            # The ID token is included in the token response
            # For now, we'll decode the access token (which is actually the ID token)
            payload = jwt.decode(access_token, options={"verify_signature": False})
            
            # Apple's user info structure
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name", {}).get("fullName", {}).get("formatted", "") if payload.get("name") else "",
                "verified_email": payload.get("email_verified", False)
            }
        except JWTError as e:
            print(f"Apple user info error: {e}")
            return None
    
    async def exchange_google_code(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange Google authorization code for access token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    async def exchange_apple_code(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange Apple authorization code for access token."""
        async with httpx.AsyncClient() as client:
            try:
                # Apple's token endpoint
                response = await client.post(
                    "https://appleid.apple.com/auth/token",
                    data={
                        "client_id": self.apple_client_id,
                        "client_secret": self.apple_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Apple token exchange error: {e}")
                return None
    
    def get_or_create_user(self, provider: str, provider_id: str, email: str, name: str = None) -> User:
        """Get existing user or create new user from OAuth provider."""
        db = SessionLocal()
        try:
            # Try to find existing user
            user = db.query(User).filter(
                User.provider == provider,
                User.provider_id == provider_id
            ).first()
            
            if user:
                # Update last login
                user.last_login = datetime.now(timezone.utc)
                db.commit()
                return user
            
            # Create new user
            user = User(
                email=email,
                name=name or email.split('@')[0],
                provider=provider,
                provider_id=provider_id,
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
                last_login=datetime.now(timezone.utc)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
    
    def create_user_session(self, user: User) -> Dict[str, Any]:
        """Create a user session with access token."""
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "provider": user.provider,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        }


# Global auth service instance
auth_service = AuthService()
