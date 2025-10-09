"""Main FastAPI application for AirPuff."""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_timescaledb
from .api.v1 import airports, weather, routes, auth, users, realtime, grafana, imessage, migration
from .api.curl.v1 import airports as curl_airports, weather as curl_weather, routes as curl_routes
from .services.websocket_manager import WebSocketManager
from .services.realtime_service import realtime_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AirPuff application...")
    init_timescaledb()
    logger.info("TimescaleDB initialized")
    
    # Start real-time service
    await realtime_service.start()
    logger.info("Real-time service started")
    
    yield
    
    # Shutdown
    await realtime_service.stop()
    logger.info("Real-time service stopped")
    logger.info("Shutting down AirPuff application...")


# Create FastAPI application
app = FastAPI(
    title="AirPuff API",
    description="Modern weather information system for aviation",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://airpuff.info"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# WebSocket manager
ws_manager = WebSocketManager()

# Include API routers
app.include_router(airports.router, prefix="/api/v1/airports", tags=["airports"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(realtime.router, prefix="/api/v1/realtime", tags=["realtime"])
app.include_router(grafana.router, prefix="/api/v1/grafana", tags=["grafana"])
app.include_router(imessage.router, prefix="/api/v1/imessage", tags=["imessage"])
app.include_router(migration.router, prefix="/api/v1/migration", tags=["migration"])

# Include cURL-friendly routers
app.include_router(curl_airports.router, prefix="/curl/v1/airports", tags=["curl-airports"])
app.include_router(curl_weather.router, prefix="/curl/v1/weather", tags=["curl-weather"])
app.include_router(curl_routes.router, prefix="/curl/v1/routes", tags=["curl-routes"])


@app.get("/")
async def root(request: Request):
    """Root endpoint - redirect to main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "api_version": "v1"}


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login - AirPuff"})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard - AirPuff"})


@app.get("/airports", response_class=HTMLResponse)
async def airports_page(request: Request):
    """Airports listing page."""
    return templates.TemplateResponse("airports.html", {"request": request, "title": "Airports - AirPuff"})


@app.get("/route-planner", response_class=HTMLResponse)
async def route_planner(request: Request):
    """Route planner page."""
    return templates.TemplateResponse("route-planner.html", {"request": request, "title": "Route Planner - AirPuff"})


@app.get("/grafana", response_class=HTMLResponse)
async def grafana_dashboards(request: Request):
    """Grafana dashboards page."""
    return templates.TemplateResponse("grafana.html", {"request": request, "title": "Grafana Dashboards - AirPuff"})


@app.get("/imessage", response_class=HTMLResponse)
async def imessage_integration(request: Request):
    """iMessage integration page."""
    return templates.TemplateResponse("imessage.html", {"request": request, "title": "iMessage Integration - AirPuff"})


@app.get("/migration", response_class=HTMLResponse)
async def migration_page(request: Request):
    """Data migration page."""
    return templates.TemplateResponse("migration.html", {"request": request, "title": "Data Migration - AirPuff"})


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(websocket, data)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)


# WebSocket endpoint with user authentication
@app.websocket("/ws/user/{user_id}")
async def websocket_user_endpoint(websocket, user_id: int):
    """WebSocket endpoint for authenticated user updates."""
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(websocket, data, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        ws_manager.disconnect(websocket, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
