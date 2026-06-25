"""Keycloak OIDC authentication endpoints.

Federates Microsoft, Google, and any other IdPs through the cloudpuff
Keycloak realm. Sessions are stored in a signed cookie via Starlette's
SessionMiddleware. Gravatar hashes are derived from the email returned
by Keycloak's userinfo and exposed to the frontend so it can build
avatar URLs client-side.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

_oauth = OAuth()
_keycloak_registered = False


def _keycloak():
    global _keycloak_registered
    if not settings.oidc_issuer:
        raise HTTPException(status_code=503, detail="OIDC is not configured")
    if not _keycloak_registered:
        _oauth.register(
            name="keycloak",
            client_id=settings.oidc_client_id,
            client_secret=settings.oidc_client_secret or "",
            server_metadata_url=f"{settings.oidc_issuer.rstrip('/')}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
        _keycloak_registered = True
    return _oauth.keycloak


def _gravatar_hash(email: str) -> str:
    e = (email or "").strip().lower()
    return hashlib.sha256(e.encode("utf-8")).hexdigest() if e else ""


def _redirect_uri() -> str:
    return settings.oidc_redirect_uri or f"{settings.base_url.rstrip('/')}/api/v1/auth/oidc/callback"


def _resolved_role(userinfo: dict) -> str:
    """Map Keycloak claims to an AirPuff role."""

    configured_roles = {
        role.strip().lower()
        for role in settings.oidc_admin_roles.split(",")
        if role.strip()
    }

    roles = set()
    top_level_roles = userinfo.get("roles")
    if isinstance(top_level_roles, list):
        roles.update(str(role).lower() for role in top_level_roles)

    realm_access = userinfo.get("realm_access") or {}
    realm_roles = realm_access.get("roles") or []
    roles.update(str(role).lower() for role in realm_roles)

    resource_access = userinfo.get("resource_access") or {}
    client_roles = (
        resource_access.get(settings.oidc_client_id, {}).get("roles") or []
    )
    roles.update(str(role).lower() for role in client_roles)

    return "admin" if configured_roles.intersection(roles) else "user"


@router.get("/login")
async def login(request: Request):
    return await _keycloak().authorize_redirect(request, _redirect_uri())


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await _keycloak().authorize_access_token(request)
    except OAuthError as exc:
        logger.warning("OIDC callback failed: %s", exc)
        raise HTTPException(status_code=400, detail="OIDC callback failed")

    userinfo = token.get("userinfo") or {}
    sub = userinfo.get("sub")
    if not sub:
        raise HTTPException(status_code=400, detail="OIDC userinfo missing sub")

    email = userinfo.get("email") or ""
    name = userinfo.get("name") or userinfo.get("preferred_username") or ""
    email_verified = bool(userinfo.get("email_verified", False))
    role = _resolved_role(userinfo)
    now = datetime.now(timezone.utc)

    user = (
        db.query(User)
        .filter(User.provider == "keycloak", User.provider_id == sub)
        .first()
    )
    if user is None:
        user = User(
            email=email,
            name=name,
            provider="keycloak",
            provider_id=sub,
            role=role,
            is_active=True,
            is_verified=email_verified,
            created_at=now,
            last_login=now,
        )
        db.add(user)
    else:
        if email:
            user.email = email
        if name:
            user.name = name
        user.role = role
        user.is_verified = email_verified or user.is_verified
        user.last_login = now
    db.commit()
    db.refresh(user)

    request.session["user"] = {
        "id": user.id,
        "sub": sub,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }
    return RedirectResponse(url="/", status_code=302)


@router.get("/me")
async def me(request: Request):
    sess = request.session.get("user")
    if not sess:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": sess.get("id"),
        "email": sess.get("email"),
        "name": sess.get("name"),
        "role": sess.get("role"),
        "is_admin": sess.get("role") == "admin",
        "gravatar_hash": _gravatar_hash(sess.get("email", "")),
    }


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    if not settings.oidc_issuer:
        return RedirectResponse(url=settings.base_url or "/", status_code=302)
    end_session = (
        f"{settings.oidc_issuer.rstrip('/')}/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={settings.base_url}"
        f"&client_id={settings.oidc_client_id}"
    )
    return RedirectResponse(url=end_session, status_code=302)
