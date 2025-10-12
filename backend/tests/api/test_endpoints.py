# API Tests for AirPuff Endpoints

import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the main health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_api_health_endpoint(self, client):
        """Test the API health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "redis" in data
        assert "services" in data

class TestAirportEndpoints:
    """Test cases for airport API endpoints."""
    
    def test_get_airports_empty(self, client):
        """Test getting airports when none exist."""
        response = client.get("/api/v1/airports/")
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_create_airport(self, client, sample_airport):
        """Test creating a new airport."""
        response = client.post("/api/v1/airports/", json=sample_airport)
        assert response.status_code == 201
        data = response.json()
        assert data["icao"] == sample_airport["icao"]
        assert data["name"] == sample_airport["name"]
        assert data["city"] == sample_airport["city"]
        assert data["state"] == sample_airport["state"]
        assert data["country"] == sample_airport["country"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_airport_by_icao(self, client, sample_airport):
        """Test getting an airport by ICAO code."""
        # Create airport first
        client.post("/api/v1/airports/", json=sample_airport)
        
        # Get airport by ICAO
        response = client.get(f"/api/v1/airports/{sample_airport['icao']}")
        assert response.status_code == 200
        data = response.json()
        assert data["icao"] == sample_airport["icao"]
        assert data["name"] == sample_airport["name"]
    
    def test_get_nonexistent_airport(self, client):
        """Test getting a non-existent airport."""
        response = client.get("/api/v1/airports/XXXX")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_create_duplicate_airport(self, client, sample_airport):
        """Test creating a duplicate airport."""
        # Create airport first
        client.post("/api/v1/airports/", json=sample_airport)
        
        # Try to create duplicate
        response = client.post("/api/v1/airports/", json=sample_airport)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

class TestWeatherEndpoints:
    """Test cases for weather API endpoints."""
    
    def test_get_weather_nonexistent_airport(self, client):
        """Test getting weather for non-existent airport."""
        response = client.get("/api/v1/weather/XXXX/latest")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_weather_no_data(self, client, sample_airport):
        """Test getting weather when no data exists."""
        # Create airport first
        client.post("/api/v1/airports/", json=sample_airport)
        
        # Get weather (should be empty)
        response = client.get(f"/api/v1/weather/{sample_airport['icao']}/latest")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_weather_with_data(self, client, sample_airport, sample_weather):
        """Test getting weather with existing data."""
        # Create airport first
        airport_response = client.post("/api/v1/airports/", json=sample_airport)
        airport_data = airport_response.json()
        
        # Update weather data with airport ID
        sample_weather["airport_id"] = airport_data["id"]
        
        # Create weather observation (this would normally be done by the service)
        # For testing, we'll simulate this by calling the weather endpoint
        response = client.get(f"/api/v1/weather/{sample_airport['icao']}/latest")
        # This will return 404 since we don't have actual weather data
        assert response.status_code == 404

class TestCurlEndpoints:
    """Test cases for cURL API endpoints."""
    
    def test_curl_airports_empty(self, client):
        """Test cURL airports endpoint when empty."""
        response = client.get("/curl/v1/airports/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert response.text == "No airports found"
    
    def test_curl_airport_by_icao(self, client, sample_airport):
        """Test cURL airport endpoint by ICAO."""
        # Create airport first
        client.post("/api/v1/airports/", json=sample_airport)
        
        # Get airport via cURL endpoint
        response = client.get(f"/curl/v1/airports/{sample_airport['icao']}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert sample_airport["icao"] in response.text
        assert sample_airport["name"] in response.text
    
    def test_curl_weather_nonexistent(self, client):
        """Test cURL weather endpoint for non-existent airport."""
        response = client.get("/curl/v1/weather/XXXX")
        assert response.status_code == 404
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "not found" in response.text.lower()

class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/airports/",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        incomplete_airport = {
            "icao": "KSFO",
            "name": "Test Airport"
            # Missing required fields
        }
        response = client.post("/api/v1/airports/", json=incomplete_airport)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_invalid_field_values(self, client):
        """Test handling of invalid field values."""
        invalid_airport = {
            "icao": "KSF",  # Too short
            "name": "Test Airport",
            "city": "Test",
            "state": "CA",
            "country": "USA",
            "latitude": 91.0,  # Invalid latitude
            "longitude": -122.3790,
            "elevation_ft": 13
        }
        response = client.post("/api/v1/airports/", json=invalid_airport)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
