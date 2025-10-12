"""Grafana API service for dashboard management."""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GrafanaService:
    """Service for interacting with Grafana API."""
    
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.username = "admin"
        self.password = "admin"
        self.api_key = None
        self.timeout = 30
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Grafana API."""
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        else:
            # Use basic auth
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {"Authorization": f"Basic {credentials}"}
    
    async def test_connection(self) -> bool:
        """Test connection to Grafana."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.get(f"{self.base_url}/api/health", headers=headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error testing Grafana connection: {e}")
            return False
    
    async def get_dashboards(self) -> List[Dict[str, Any]]:
        """Get list of dashboards."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.get(f"{self.base_url}/api/search?type=dash-db", headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting dashboards: {e}")
            return []
    
    async def get_dashboard(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get specific dashboard by UID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.get(f"{self.base_url}/api/dashboards/uid/{uid}", headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting dashboard {uid}: {e}")
            return None
    
    async def create_dashboard(self, dashboard: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new dashboard."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                payload = {
                    "dashboard": dashboard,
                    "overwrite": True
                }
                response = await client.post(f"{self.base_url}/api/dashboards/db", 
                                            json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None
    
    async def get_datasources(self) -> List[Dict[str, Any]]:
        """Get list of datasources."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.get(f"{self.base_url}/api/datasources", headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting datasources: {e}")
            return []
    
    async def create_datasource(self, datasource: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new datasource."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.post(f"{self.base_url}/api/datasources", 
                                           json=datasource, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating datasource: {e}")
            return None
    
    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get alert rules."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.get(f"{self.base_url}/api/ruler/grafana/api/v1/rules", headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting alert rules: {e}")
            return []
    
    async def create_alert_rule(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an alert rule."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = await self._get_auth_headers()
                response = await client.post(f"{self.base_url}/api/ruler/grafana/api/v1/rules", 
                                           json=rule, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating alert rule: {e}")
            return None
    
    async def get_dashboard_url(self, uid: str) -> str:
        """Get URL for a dashboard."""
        return f"{self.base_url}/d/{uid}"
    
    async def get_dashboard_embed_url(self, uid: str, theme: str = "dark") -> str:
        """Get embed URL for a dashboard."""
        return f"{self.base_url}/d/{uid}?theme={theme}&kiosk"
    
    async def create_weather_alert_rule(self, airport_icao: str) -> Optional[Dict[str, Any]]:
        """Create a weather alert rule for an airport."""
        rule = {
            "alert": {
                "name": f"Weather Alert - {airport_icao}",
                "message": f"Weather conditions at {airport_icao} require attention",
                "frequency": "10s",
                "conditions": [
                    {
                        "evaluator": {
                            "params": [3],
                            "type": "gt"
                        },
                        "operator": {
                            "type": "and"
                        },
                        "query": {
                            "params": ["A", "5m", "now"]
                        },
                        "reducer": {
                            "params": [],
                            "type": "last"
                        },
                        "type": "query"
                    }
                ],
                "executionErrorState": "alerting",
                "for": "5m",
                "noDataState": "no_data",
                "handler": 1
            },
            "dashboardId": None,
            "panelId": None,
            "name": f"Weather Alert - {airport_icao}",
            "message": f"Weather conditions at {airport_icao} require attention"
        }
        
        return await self.create_alert_rule(rule)
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get Grafana service statistics."""
        try:
            dashboards = await self.get_dashboards()
            datasources = await self.get_datasources()
            alert_rules = await self.get_alert_rules()
            
            return {
                "connected": await self.test_connection(),
                "dashboards_count": len(dashboards),
                "datasources_count": len(datasources),
                "alert_rules_count": len(alert_rules),
                "base_url": self.base_url,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting Grafana stats: {e}")
            return {
                "connected": False,
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat()
            }


# Global Grafana service instance
grafana_service = GrafanaService()
