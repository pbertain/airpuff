"""Grafana API endpoints for dashboard management."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...api.v1.auth import get_current_user
from ...services.grafana_service import grafana_service

router = APIRouter()


@router.get("/status")
async def get_grafana_status():
    """Get Grafana service status."""
    try:
        stats = await grafana_service.get_service_stats()
        return {
            "status": "connected" if stats.get("connected") else "disconnected",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Grafana status: {str(e)}")


@router.get("/dashboards")
async def get_dashboards():
    """Get list of Grafana dashboards."""
    try:
        dashboards = await grafana_service.get_dashboards()
        return {
            "dashboards": dashboards,
            "count": len(dashboards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboards: {str(e)}")


@router.get("/dashboards/{uid}")
async def get_dashboard(uid: str):
    """Get specific dashboard by UID."""
    try:
        dashboard = await grafana_service.get_dashboard(uid)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")


@router.get("/dashboards/{uid}/url")
async def get_dashboard_url(uid: str, embed: bool = False):
    """Get URL for a dashboard."""
    try:
        if embed:
            url = await grafana_service.get_dashboard_embed_url(uid)
        else:
            url = await grafana_service.get_dashboard_url(uid)
        
        return {
            "uid": uid,
            "url": url,
            "embed": embed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard URL: {str(e)}")


@router.get("/datasources")
async def get_datasources():
    """Get list of Grafana datasources."""
    try:
        datasources = await grafana_service.get_datasources()
        return {
            "datasources": datasources,
            "count": len(datasources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting datasources: {str(e)}")


@router.get("/alerts")
async def get_alert_rules():
    """Get Grafana alert rules."""
    try:
        alerts = await grafana_service.get_alert_rules()
        return {
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert rules: {str(e)}")


@router.post("/alerts/weather/{airport_icao}")
async def create_weather_alert(
    airport_icao: str,
    current_user: User = Depends(get_current_user)
):
    """Create a weather alert rule for an airport."""
    try:
        alert_rule = await grafana_service.create_weather_alert_rule(airport_icao.upper())
        if not alert_rule:
            raise HTTPException(status_code=500, detail="Failed to create alert rule")
        
        return {
            "message": f"Weather alert created for {airport_icao.upper()}",
            "airport": airport_icao.upper(),
            "alert_rule": alert_rule
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating weather alert: {str(e)}")


@router.get("/weather-dashboard")
async def get_weather_dashboard_url():
    """Get URL for the weather dashboard."""
    try:
        url = await grafana_service.get_dashboard_url("airpuff-weather")
        return {
            "dashboard": "Weather Dashboard",
            "uid": "airpuff-weather",
            "url": url,
            "description": "Real-time weather trends and statistics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weather dashboard URL: {str(e)}")


@router.get("/airport-dashboard")
async def get_airport_dashboard_url(airport: str = Query(..., description="Airport ICAO code")):
    """Get URL for the airport-specific dashboard."""
    try:
        url = await grafana_service.get_dashboard_url("airport-weather")
        # Add airport parameter to URL
        url_with_param = f"{url}?var-airport={airport.upper()}"
        
        return {
            "dashboard": "Airport Weather Dashboard",
            "uid": "airport-weather",
            "airport": airport.upper(),
            "url": url_with_param,
            "description": f"Weather trends and statistics for {airport.upper()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting airport dashboard URL: {str(e)}")


@router.get("/embed/weather")
async def get_weather_dashboard_embed():
    """Get embed URL for the weather dashboard."""
    try:
        url = await grafana_service.get_dashboard_embed_url("airpuff-weather")
        return {
            "dashboard": "Weather Dashboard (Embedded)",
            "uid": "airpuff-weather",
            "url": url,
            "embed": True,
            "description": "Embeddable weather dashboard"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weather dashboard embed URL: {str(e)}")


@router.get("/embed/airport")
async def get_airport_dashboard_embed(airport: str = Query(..., description="Airport ICAO code")):
    """Get embed URL for the airport-specific dashboard."""
    try:
        url = await grafana_service.get_dashboard_embed_url("airport-weather")
        # Add airport parameter to URL
        url_with_param = f"{url}&var-airport={airport.upper()}"
        
        return {
            "dashboard": "Airport Weather Dashboard (Embedded)",
            "uid": "airport-weather",
            "airport": airport.upper(),
            "url": url_with_param,
            "embed": True,
            "description": f"Embeddable weather dashboard for {airport.upper()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting airport dashboard embed URL: {str(e)}")
